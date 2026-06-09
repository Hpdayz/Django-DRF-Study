# -*- coding: utf-8 -*-
'''
微步在线 IP 信誉查询接口
支持 GET / POST
参数：resource (必填), lang (可选), cache (可选), realtime_verdict (可选)
'''

import copy
import json
from datetime import timedelta

import redis
import requests
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import ThreatBookConfig, ThreatBookCache


# ---------- 常量 ----------
BASEURL = 'https://api.threatbook.cn/v3/scene/ip_reputation'  # 微步官方
# BASEURL = 'http://127.0.0.1:8000/threatbook/mock/ip_reputation'  # 本地 mock

CACHE_TTL = 3600
REDIS_URL = 'redis://:Hpday@8.136.200.128:6379/1'

# mock 基础数据
MOCK_DATA = {
    'response_code': 0,
    'verbose_msg': 'Ok',
    'data': {
        '__RESOURCE__': {
            'basic': {
                'carrier': 'China Telecom',
                'location': {
                    'country': '中国', 'country_code': 'CN',
                    'province': '福建省', 'lng': '118.55754',
                    'city': '泉州市', 'lat': '24.902359',
                },
            },
            'asn': {'number': 4134, 'rank': 4, 'info': 'CHINANET-BACKBONE'},
            'confidence_level': 'high',
            'is_malicious': True,
            'severity': 'medium',
            'judgments': ['动态IP', '僵尸网络', '垃圾邮件', 'IoT设备'],
            'update_time': '2024-10-17 14:29:48',
            'scene': '住宅',
            'tags_classes': [],
            'entity': [],
            'evaluation': {'active': 'low', 'honeypot_hit': True},
            'feature': [],
            'hist_behavior': [{
                'category': '扫描',
                'tag_desc': '端口扫描是一种确定网络上哪些端口处于打开状态并且可以接收或发送数据的方法。',
                'tag_name': '端口扫描',
                'vuln_id': [],
            }],
            'permalink': '__PERMALINK__',
        }
    },
}

_redis_client = None


def _build_mock_data(resource):
    data = copy.deepcopy(MOCK_DATA)
    ip_data = data['data'].pop('__RESOURCE__')
    ip_data['permalink'] = f'https://x.threatbook.com/v5/ip/{resource}'
    data['data'][resource] = ip_data
    return data


# ═══════════════════════════════════════════════════════
#  Mock 接口 —— 模拟微步官方 API 返回（B 接口）
# ═══════════════════════════════════════════════════════

@api_view(['GET'])
def mock_ip_reputation(request):
    resource = request.query_params.get('resource', '0.0.0.0')
    return Response(_build_mock_data(resource))


# ═══════════════════════════════════════════════════════
#  IP 信誉查询接口（A 接口）
# ═══════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
def ip_reputation(request):
    # ── 取参数 ──
    if request.method == 'GET':
        resource = request.query_params.get('resource')
        lang = request.query_params.get('lang', 'zh')
        use_cache = request.query_params.get('cache', 'true').lower() != 'false'
        realtime_verdict = request.query_params.get('realtime_verdict', 'false').lower() in ('true', '1')
    else:
        resource = request.data.get('resource')
        lang = request.data.get('lang', 'zh')
        use_cache = request.data.get('cache', True)
        if isinstance(use_cache, str):
            use_cache = use_cache.lower() != 'false'
        rd_val = request.data.get('realtime_verdict', False)
        if isinstance(rd_val, str):
            realtime_verdict = rd_val.lower() in ('true', '1')
        else:
            realtime_verdict = bool(rd_val)

    if not resource:
        return Response(
            {'response_code': 1, 'verbose_msg': 'resource 参数缺失'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def cache_key():
        return f'threatbook:ip:{resource}:{lang}'

    def get_redis():
        global _redis_client
        if _redis_client is None:
            _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        return _redis_client

    # ── cache=true → Redis → DB → API ──
    if use_cache:
        # 1) Redis
        try:
            r = get_redis()
            cached = r.get(cache_key())
            if cached is not None:
                print("使用 Redis 缓存结果")
                return Response(json.loads(cached))
        except redis.RedisError:
            pass

        # # 2) DB
        # cutoff = now() - timedelta(seconds=CACHE_TTL)
        # db_cached = (
        #     ThreatBookCache.objects
        #     .filter(resource=resource, lang=lang, created_at__gte=cutoff)
        #     .order_by('-created_at')
        #     .first()
        # )
        # if db_cached is not None:
        #     try:
        #         r.setex(cache_key(), CACHE_TTL, db_cached.response_data)
        #     except redis.RedisError:
        #         pass
        #     return Response(json.loads(db_cached.response_data))

    # ── 缓存 miss / cache=false → 调 API（当前为本地 mock）──
    try:
        config = ThreatBookConfig.objects.get(key='apikey')
        apikey = config.value
    except ThreatBookConfig.DoesNotExist:
        return Response(
            {'response_code': 2, 'verbose_msg': '数据库中未配置 apikey'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        resp = requests.get(
            BASEURL,
            params={
                'apikey': apikey,
                'resource': resource,
                'lang': lang,
                'realtime_verdict': str(realtime_verdict).lower(),
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return Response(
            {'response_code': 3, 'verbose_msg': f'API 调用失败: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # ── 成功才入库 + 入 Redis ──
    if data.get('response_code') == 0:
        data_str = json.dumps(data, ensure_ascii=False)
        # ThreatBookCache.objects.create(
        #     resource=resource, lang=lang, response_data=data_str,
        # )
        try:
            r = get_redis()
            r.setex(cache_key(), CACHE_TTL, data_str)
        except redis.RedisError:
            pass

    return Response(data)
