## request 对象
    - oop 相关
### 类中的 `__getattr__` 什么时候触发？
    - 对象中有的成员，不会触发
    - 对象中无的成员，会触发
```python
class Foo(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def show(self):
        return "xx"
    def __getattr__(self, item):
        print("--->", item)
        return 99
obj = Foo('Hpday', 24)
# 获取成员 方法1
# print(obj.name)
# print(obj.age)
# print(obj.show())
# 获取成员 方法2
# v1 = getattr(obj, 'name')
# print(v1)

# 不触发 __getattr__
obj.name
obj.age
obj.show()

# 触发 __getattr__
obj.xxx
```

### 类中的 `__getattribute__` 什么时候触发?
    - 只要执行 '对象.xxx' 都会执行 `__getattribute__`
    - object 中的 `__getattribute__` 内部处理机制
        - 对象中有值，返回
        - 对象中无值，报错
```python
class Foo(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def show(self):
        pass
        return "xx"

    # def __getattr__(self, item):
    #     print("--->", item)
    #     return 99

    def __getattribute__(self, item):
        print('--->', item)
        return 99
obj = Foo('Hpday', 24)
obj.name
obj.age
obj.show
```
### 案例分析
```python
class HttpResponse(object):
    def __init__(self):
        pass
    def v1(self):
        print('v1')
    def v2(self):
        print('v2')
class Request(object):
    def __init__(self, req, xx):
        self._request = req
        self.xx = xx
    def __getattr__(self, item):
        try:
            return getattr(self._request, item)
        except AttributeError:
            return self.__getattribute__(item)
            # return '你好'
req = HttpResponse()
req.v1()
req.v2()

request = Request(req, "Hpday")
request._request.v1()
request.v2()
print(request.v3)
```
    - drf 请求流程

    - 请求参数
        *, args**kwargs
        v1, v2, v3

## 认证组件
    - 直接用，用户授权
        示例1
        - 100 个 API，1个无需登录；其他需要登录
        - 实现
            - 编写类 -> 认证组件
            - 应用组件（局部）
        示例2
        - 100 个 API，1个无需登录；其他需要登录 （全局配置）
        - 实现
            - 编写类 -> 认证组件
            - 应用组件（全局）
            REST_FRAMEWORK= {
                "UNAUTHENTICATED_USER": None
                "DEFAULT_AUTHENTICATION_CLASSES": ["app01_认证.views.MyAuthentication"]
            }
        在 drf 中，先从全局中找，再从局部中找
        全局配置时， 认证组件不能写在 views 视图中,会触发循环引用问题
    - 面向对象-继承
```python
class APIView(object):
    authentication_classes = 读取配置文件中的列表
    def dispatch(self):
        self.authentication_classes
class UserView(APIView):
    authentication_classes = ['xx']
obj = UserView()
obj.dispatch()
```
    - 认证源码分析
        -> 从 APIView 开始一步一步看（后续分析）
    - 知识点
        - 多个认证类
            - 都返回 None，都没有认证成功 -> 视图是否会被执行？ 视图函数会执行，只不过 self.user  self.auth = None
        - 状态码一致
            - 和 rest_framework 的 BaseAuthentication 
                def authenticate_header(self, request): 相关
    - 扩展，python 开发 -> 子类约束
```python
class C1(object):
    def fn1(self):
        raise NotImplementedError("fn1() must be overridden")
class C2(C1):
    def fn1(self):
        pass
```
## 案例：用户登录 + 用户认证
    POST http://127.0.0.1:8000/login/       用户名和密码  ->  JSON
    {
        "username": "Hpday",
        "password":"123"
    }
    {
        "status": true,
        "msg": "OK",
        "token": "9812cd1d-56da-45c8-9eda-ec973fc1c056"
    }
    GET http://127.0.0.1:8000/app01/user/?token=xx   请求头或URL 中携带 token
        - 请求头 GET   http://127.0.0.1:8000/app01/user/
                      Authorization: a5476a0d
                DRF 读取 "token = request.headers.get("Authorization")"
                        "token = request.META.get("HTTP_AUTHORIZATION")"
        - URL   GET http://127.0.0.1:8000/app01/user/?token=a5476a0d
                DRF 读取 "token = request.query_params.get("token")"

## 权限组件
    认证组件 = [认证类1, 认证类2, 认证类3, ... ]  -> 执行每个认证类中的 authenticate 方法
                                                    - 认证成功或失败，不会执行后续的认证类
                                                    - 返回None，执行后续的认证类
    
    项目中某个请求必须满足：A条件 && B条件 && C条件
    权限组件 = [权限类1, 权限类2, 权限类3, ... ]  -> 执行所有权限类的 has_permission 方法，返回 True 通过，返回 False 失败
                                                    - 执行所有的权限类
                                                    - 学会源码流程，扩展 + 自定义
    - 实现
        - 编写类 -> 认证组件
        - 应用组件（局部）