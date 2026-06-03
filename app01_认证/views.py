import uuid

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

# 编写认证组件
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

# 导入数据库模型
from app01_认证.models import UserInfo
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
            raise AuthenticationFailed({'status': 401, 'message': "无token"})
        # 校验合法性
        user_obj = UserInfo.objects.filter(token=token).first()
        if user_obj:
            return user_obj, token

        # return

        # if token:
        #     print('认证组件', token)
        #     return 'Hpday', token
        raise AuthenticationFailed({'status': 403, 'message': "认证失败"})
    def authenticate_header(self, request):
        return "API"

class LoginView(APIView):
    def get(self, request):
        return Response('LoginView')

    def post(self, request):
        # 1.接收用户提交的用户名和密码
        # print(request._request.body)
        # print(request.data) # 获取 Body 参数
        # print(request.query_params) # 获取路径参数

        # 2.数据库校验
        user = request.data.get('username')
        pwd = request.data.get('password')
        user_obj = UserInfo.objects.filter(username=user, password=pwd).first()
        if not user_obj:
            return Response({"status": False, "msg": '用户名或密码错误'})
        token = str(uuid.uuid4())
        user_obj.token = token
        user_obj.save()
        return Response({"status": True, "msg": 'OK', "token": token})

class UserView(APIView):
    authentication_classes = [ MyAuthentication, ]
    def get(self, request):
        print(request.user.username, request.auth)
        return Response('UserView')
