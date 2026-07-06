"""S6000 HMAC-SHA256 签名模块。

认证流程:
  1. 生成 yyyyMMddHHmmssSSS 格式的毫秒时间戳
  2. signature = hex(HmacSHA256(timestamp, secretKey))
  3. Authorization = "Basic " + Base64(appCode + ":" + signature)
"""
import base64
import hashlib
import hmac
from datetime import datetime


def generate_timestamp() -> str:
    """返回 yyyyMMddHHmmssSSS 格式的当前毫秒时间戳（17 位）。"""
    return datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]


def hmac_sha256_sign(data: str, secret_key: str) -> str:
    """对 data 做 HmacSHA256 签名，返回 hex 字符串（小写）。"""
    mac = hmac.new(
        secret_key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256,
    )
    return mac.hexdigest()


def build_authorization(app_code: str, secret_key: str, timestamp: str) -> str:
    """拼装完整的 Authorization header 值。

    signature = hex(HmacSHA256(timestamp, secretKey))
    Authorization = "Basic " + Base64(appCode + ":" + signature)
    """
    signature = hmac_sha256_sign(timestamp, secret_key)
    credentials = f'{app_code}:{signature}'
    encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return f'Basic {encoded}'
