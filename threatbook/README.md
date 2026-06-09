# threatbook 模块说明

## 概述

新建 `threatbook` Django app，提供微步在线 IP 信誉查询的模拟接口。当前阶段因无 API Key，接口返回符合官方格式的 mock 数据，并集成 Redis 缓存。

## 新增/修改文件

| 文件 | 说明 |
|------|------|
| `threatbook/__init__.py` | 空白包文件 |
| `threatbook/apps.py` | App 配置，`ThreatBookConfig` |
| `threatbook/views.py` | 核心视图，IP 信誉查询接口 |
| `threatbook/urls.py` | 路由注册 |
| `DRF/settings.py` | 新增 `THREATBOOK_CACHE_TTL`、`THREATBOOK_API_KEY` 配置项；`INSTALLED_APPS` 中注册 `threatbook` |
| `DRF/urls.py` | 注册 threatbook 路由 |
| `pyproject.toml` | 新增 `django-redis` 依赖 |

## 接口说明

### IP 信誉查询

```
POST /threatbook/ip/reputation
Content-Type: application/json
```

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| resource | string | 是 | IP 地址 |
| lang | string | 否 | 语言，zh/en，默认 zh |
| realtime_verdict | int | 否 | 1=强制实时查询（跳过缓存），默认 0 |

**请求示例：**

```json
{
    "resource": "1.2.3.4"
}
```

**返回格式（与微步官方一致）：**

```json
{
    "response_code": 0,
    "verbose_msg": "Ok",
    "data": {
        "1.2.3.4": {
            "basic": { "carrier": "...", "location": {...} },
            "asn": { "number": 4134, "rank": 4, "info": "..." },
            "confidence_level": "high",
            "is_malicious": true,
            "severity": "medium",
            "judgments": ["动态IP", "僵尸网络", "..."],
            "update_time": "...",
            "scene": "住宅",
            "permalink": "https://x.threatbook.com/v5/ip/1.2.3.4"
        }
    }
}
```

## Redis 缓存策略

- 缓存 Key：`threatbook:ip:{resource}`
- 缓存 TTL：3600 秒（1 小时），可通过 `CACHE_TTL` 变量修改
- 默认请求先查缓存，命中则直接返回
- `realtime_verdict=1` 时强制跳过缓存，查完后更新缓存
- Redis 连接配置在 `views.py` 顶部（HOST / PORT / PASSWORD / DB），当前指向 Hpday 服务器

## 后续接入真实 API

在 `views.py` 的 `ip_reputation` 函数中，找到 `TODO` 注释处，将 mock 调用替换为：

```python
url = "https://api.threatbook.cn/v3/scene/ip_reputation"
resp = requests.get(url, params={"apikey": apikey, "resource": resource, "lang": lang})
data = resp.json()
```

apikey 建议从 `settings.THREATBOOK_API_KEY` 读取，该配置项后续可改为从数据库 GlobalConfig 动态获取。
