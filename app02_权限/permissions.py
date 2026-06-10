from rest_framework.permissions import BasePermission

class MyPermission1(BasePermission):
    message = {"status": False, "msg": "无权访问1"}
    def has_permission(self, request, view):
        print("my_permission1")
        return False

class MyPermission2(BasePermission):
    message = {"status": False, "msg": "无权访问2"}
    def has_permission(self, request, view):
        print("my_permission2")
        return True

class MyPermission3(BasePermission):
    message = {"status": False, "msg": "无权访问3"}
    def has_permission(self, request, view):
        print("my_permission3")
        return True

class UserPermission(BasePermission):
    message = {"status": False, "msg": "用户无权访问"}
    def has_permission(self, request, view):
        if request.user.role == 3:
            return True
        return False

class ManagePermission(BasePermission):
    message = {"status": False, "msg": "管理无权访问"}

    def has_permission(self, request, view):
        if request.user.role == 2:
            return True
        return False

class BossPermission(BasePermission):
    message = {"status": False, "msg": "总监无权访问"}

    def has_permission(self, request, view):
        if request.user.role == 1:
            return True
        return False