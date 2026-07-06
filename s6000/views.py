# -*- coding: utf-8 -*-
"""S6000 API proxy views.

POST /s6000/intelligence - proxy the intelligence API with Redis caching.
"""
import json

import redis
import requests
from rest_framework import permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
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


def _get_config(key):
    try:
        return S6000Config.objects.get(key=key).value
    except S6000Config.DoesNotExist:
        raise ValueError('missing config: {}'.format(key))


def _cache_key(ip):
    return 's6000:intelligence:{}'.format(ip)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def intelligence(request):
    ip = request.data.get('ip')
    if not ip:
        return Response(
            {'code': 400, 'msg': 'ip missing'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        cached = _get_redis().get(_cache_key(ip))
        if cached is not None:
            return Response(json.loads(cached))
    except redis.RedisError:
        pass

    try:
        app_code = _get_config('appCode')
        secret_key = _get_config('secretKey')
        base_url = _get_config('baseUrl')
    except ValueError as e:
        return Response(
            {'code': 500, 'msg': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    timestamp = generate_timestamp()
    authorization = build_authorization(app_code, secret_key, timestamp)

    url = '{}/s6000-configuration/mortani/getIntelligenceData'.format(base_url)
    headers = {
        'Content-Type': 'application/json',
        'Timestamp': timestamp,
        'Authorization': authorization,
    }

    try:
        resp = requests.post(url, json={'ip': ip}, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return Response(
            {'code': 502, 'msg': 'API call failed: {}'.format(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if data.get('code') == 200:
        try:
            _get_redis().setex(
                _cache_key(ip), CACHE_TTL,
                json.dumps(data, ensure_ascii=False),
            )
        except redis.RedisError:
            pass

    return Response(data)
