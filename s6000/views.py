# -*- coding: utf-8 -*-
"""S6000 API proxy views.

POST /s6000/intelligence - proxy the intelligence API with Redis caching.
"""
import json

import redis
import requests
from rest_framework import permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .models import S6000Config
from .signature import build_authorization, generate_timestamp

REDIS_URL = "redis://:Hpday@8.136.200.128:6379/1"
CACHE_TTL = 3600

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


def _get_config(key):
    try:
        return S6000Config.objects.get(key=key).value
    except S6000Config.DoesNotExist:
        raise ValueError("missing config: {}".format(key))


def _cache_key(ip):
    return "s6000:intelligence:{}".format(ip)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def intelligence(request):
    ip = request.data.get("ip")
    if not ip:
        return Response({
            "code": 10400,
            "data": None,
            "message": "ip 参数缺失",
        })

    try:
        cached = _get_redis().get(_cache_key(ip))
        if cached is not None:
            data = json.loads(cached)
            return Response({
                "code": 10200,
                "data": data,
                "message": "success",
            })
    except redis.RedisError:
        pass

    try:
        app_code = _get_config("appCode")
        secret_key = _get_config("secretKey")
        base_url = _get_config("baseUrl")
    except ValueError as e:
        return Response({
            "code": 10400,
            "data": None,
            "message": "配置缺失: {}".format(e),
        })

    timestamp = generate_timestamp()
    authorization = build_authorization(app_code, secret_key, timestamp)

    url = "{}/s6000-configuration/mortani/getIntelligenceData".format(base_url)
    headers = {
        "Content-Type": "application/json",
        "Timestamp": timestamp,
        "Authorization": authorization,
    }

    try:
        resp = requests.post(url, json={"ip": ip}, headers=headers, timeout=15)
        resp.raise_for_status()
        raw = resp.json()
    except requests.RequestException as e:
        return Response({
            "code": 10400,
            "data": None,
            "message": "接口调用失败: {}".format(e),
        })

    if raw.get("code") == 200:
        try:
            _get_redis().setex(
                _cache_key(ip), CACHE_TTL,
                json.dumps(raw, ensure_ascii=False),
            )
        except redis.RedisError:
            pass

    return Response({
        "code": 10200,
        "data": raw,
        "message": "success",
    })



# ═══════════════════════════════════════════════════════
#  新增：intelligence_gc（参考线上 Threatbook ip_reputation 模式）
#  - 配置走 GlobalConfig（gcget），不再读 S6000Config 表
#  - 签名、Redis、缓存全部内联，不拆 helper
#  - POST only
# ═══════════════════════════════════════════════════════

import base64
import hashlib
import hmac
from datetime import datetime

from apps.configuration.utils.gconf import gcget, gcset
from common.drf.response import Response as PlatformResponse


@api_view(["POST"])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def intelligence_gc(request):
    """
    S6000 情报接口（参考线上 Threatbook ip_reputation 模式）
    POST /s6000/intelligence_gc

    与原 intelligence 的区别：
      1. 配置不再读 S6000Config 表，改用 GlobalConfig（gcget）
      2. 签名、Redis、缓存逻辑全部内联，无外部 helper
      3. POST only
    """
    ip = request.data.get("ip")
    use_cache = request.data.get("use_cache", True)
    app_code = request.data.get("app_code")
    secret_key = request.data.get("secret_key")
    base_url = request.data.get("base_url")
    if isinstance(use_cache, str):
        use_cache = use_cache.lower() != "false"

    if not ip:
        return PlatformResponse(code=10400, data=None, message="ip 参数缺失")

    # -- 读缓存 --
    if use_cache:
        try:
            if _redis_client is None:
                _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            cached = _redis_client.get("s6000:intelligence:{}".format(ip))
            if cached is not None:
                return PlatformResponse(code=10200, data=json.loads(cached), message="success")
        except redis.RedisError:
            pass

    # -- 获取配置（gcget）--
    conf = gcget("S6000_CONF", default={}) or {}
    if not app_code:
        app_code = conf.get("app_code")
    if not secret_key:
        secret_key = conf.get("secret_key")
    if not base_url:
        base_url = conf.get("base_url")

    new_conf = {"app_code": app_code, "secret_key": secret_key, "base_url": base_url}
    if conf != new_conf:
        gcset("S6000_CONF", new_conf, type_="json")

    if not app_code or not secret_key or not base_url:
        return PlatformResponse(code=10400, data=None, message="S6000 配置缺失（app_code / secret_key / base_url）")

    # -- 构建签名: HMAC-SHA256 --
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    mac = hmac.new(secret_key.encode("utf-8"), timestamp.encode("utf-8"), hashlib.sha256)
    signature = mac.hexdigest()
    credentials = "{}:{}".format(app_code, signature)
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    authorization = "Basic {}".format(encoded)

    url = "{}/s6000-intelligence/mortani/getIntelligenceData".format(base_url)
    headers = {
        "Content-Type": "application/json",
        "Timestamp": timestamp,
        "Authorization": authorization,
    }

    # -- 调用 S6000 API --
    try:
        resp = requests.post(url, json={"ip": ip}, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return PlatformResponse(code=10400, data=None, message="接口调用失败: {}".format(e))
    except (ValueError, Exception):
        return PlatformResponse(code=10400, data=None, message="接口返回数据格式异常")

    # -- 成功才写缓存 --
    if data.get("code") == 200:
        try:

            if _redis_client is None:
                _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            _redis_client.setex(
                "s6000:intelligence:{}".format(ip), CACHE_TTL,
                json.dumps(data, ensure_ascii=False),
            )
        except redis.RedisError:
            pass

    return PlatformResponse(code=10200, data=data, message="success")
