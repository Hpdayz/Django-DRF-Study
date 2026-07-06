"""S6000 接口代理视图。

POST /s6000/intelligence — 代理国网情报接口，含 Redis 缓存。
"""
import json

import redis
import requests
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import S6000Config
from .signature import build_authorization, generate_timestamp

REDIS_URL = 'redis://:Hpday@8.136.200.128:6379/1'
CACHE_TTL = 3600

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


def _get_config(key: str) -> str:
    """从 DB 读取配置值，缺失时抛 ValueError。"""
    try:
        return S6000Config.objects.get(key=key).value
    except S6000Config.DoesNotExist:
        raise ValueError(f'数据库中未配置 {key}')


def _cache_key(ip: str) -> str:
    return f's6000:intelligence:{ip}'


@api_view(['POST'])
def intelligence(request):
    # 1. 校验入参
    ip = request.data.get('ip')
    if not ip:
        return Response(
            {'code': 400, 'msg': 'ip 参数缺失'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 2. 查 Redis 缓存
    try:
        cached = _get_redis().get(_cache_key(ip))
        if cached is not None:
            return Response(json.loads(cached))
    except redis.RedisError:
        pass

    # 3. 读凭证
    try:
        app_code = _get_config('appCode')
        secret_key = _get_config('secretKey')
        base_url = _get_config('baseUrl')
    except ValueError as e:
        return Response(
            {'code': 500, 'msg': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 4. 生成签名
    timestamp = generate_timestamp()
    authorization = build_authorization(app_code, secret_key, timestamp)

    # 5. 转发 S6000
    url = f'{base_url}/s6000-configuration/mortani/getIntelligenceData'
    headers = {
        'Content-Type': 'application/json',
        'Timestamp': timestamp,
        'Authorization': authorization,
    }
    body = {'ip': ip}

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return Response(
            {'code': 502, 'msg': f'API 调用失败: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # 6. 成功则缓存
    if data.get('code') == 200:
        try:
            _get_redis().setex(
                _cache_key(ip), CACHE_TTL,
                json.dumps(data, ensure_ascii=False),
            )
        except redis.RedisError:
            pass

    return Response(data)
