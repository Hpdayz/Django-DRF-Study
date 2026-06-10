import uuid

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request

from ext.auth import MyAuthentication, HeaderAuthentication
from ext.per import MyPermission1, MyPermission2, MyPermission3, UserPermission, BossPermission

# 导入数据库模型
from .models import UserInfo

class LoginView(APIView):
    authentication_classes = []

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
    # authentication_classes = [ MyAuthentication, HeaderAuthentication ]
    def get(self, request):
        print(request.user.role, request.auth)
        return Response('UserView')

class OrderView(APIView):
    permission_classes = [ MyPermission1, MyPermission2, MyPermission3 ]
    def get(self, request):
        print(request.user.username, request.auth)
        return Response({"status": True, "data": [ 11, 22, 33, 44 ]})

    # def check_permissions(self, request):
    #     no_permission_obj = []
    #     # self.dispatch()
    #     for permission in self.get_permissions():
    #         if permission.has_permission(request, self):
    #             return
    #         else:
    #             no_permission_obj.append(permission)
    #     else:
    #         self.permission_denied(
    #             request,
    #             message=getattr(no_permission_obj[0], 'message', None),
    #             code=getattr(no_permission_obj[0], 'code', None)
    #         )

class NewView(APIView):
    def check_permissions(self, request):
        no_permission_obj = []
        # self.dispatch()
        for permission in self.get_permissions():
            if permission.has_permission(request, self):
                return
            else:
                no_permission_obj.append(permission)
        else:
            self.permission_denied(
                request,
                message=getattr(no_permission_obj[0], 'message', None),
                code=getattr(no_permission_obj[0], 'code', None)
            )

class AvatarView(NewView):
    # 总监 / 员工
    permission_classes = [UserPermission, BossPermission]

    def get(self, request):
        print(request.user, request.auth)
        return Response({"status": True, "data": [1, 3]})
