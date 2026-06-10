# 编写认证组件
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# 导入数据库模型
from day01.models import UserInfo


class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 用户认证
        # 1.读取请求中传递的 token
        # 2.校验合法性
        # 3.返回值
        #   3.1 返回元组(11,22)  认证成功 request.user request.auth
        #   3.2 抛出异常         认证失败 -> 返回错误信息
        #   3.3 返回None        多个认证类 [类1，类2，类3，... ] -> 匿名用户
        token = request.query_params.get('token')
        if not token:
            # raise AuthenticationFailed({'status': 401, 'message': "无token"})
            return
        # 校验合法性
        user_obj = UserInfo.objects.filter(token=token).first()
        if user_obj:
            return user_obj, token

        # return

        # if token:
        #     print('认证组件', token)
        #     return 'Hpday', token
        # raise AuthenticationFailed({'status': 403, 'message': "认证失败"})
    def authenticate_header(self, request):
        return "API"

class HeaderAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return
        user_obj = UserInfo.objects.filter(token=token).first()
        if user_obj:
            return user_obj,token

        # raise AuthenticationFailed({"status": 401, "message": "token过期"})
    def authenticate_header(self, request):
        return 'API'

class NoAuthentication(BaseAuthentication):
    def authenticate(self, request):
        raise AuthenticationFailed({'status': 403, 'message': "未携带token"})

    def authenticate_header(self, request):
        return "API"
