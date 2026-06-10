from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

from app02_权限.permissions import MyPermission1, MyPermission2, MyPermission3, UserPermission, ManagePermission, BossPermission
from ext.auth import MyAuthentication
class OrderView(APIView):
    authentication_classes = [MyAuthentication]
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

class XinView(APIView):
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

class AvatarView(XinView):
    # 总监 / 员工
    authentication_classes = [MyAuthentication]
    permission_classes = [ UserPermission, BossPermission ]
    def get(self, request):
        print(request.user, request.auth)
        return Response({"status": True, "data": [1, 3]})

