import datetime

from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response

from day02 import models
from rest_framework import serializers

from day03 import models

from django.core import exceptions

class DepartSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class DepartView(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        # 获原始数据
        print(request.data)
        #2. 校验
        ser =DepartSerializer(data=request.data)
        # if ser.is_valid():
        #     print(ser.validated_data)
        # else:
        #     print(ser.errors)
        ser.is_valid(raise_exception=True)

        return Response("xxx")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = ["name", "age", "gender", "depart_id"]

    # def validate_depart(self, value):
    #      if value.id > 1:
    #          return value
    #      raise exceptions.ValidationError("depart_id 不可以是 1")

class UserView(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        ser = UserSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        print("视图：", ser.validated_data)
        ser.save()
        return Response("xxx")

class Dp1Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Depart
        fields = "__all__"

class Dp2Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Depart
        fields = ["title", "count"]

class DpSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Depart
        fields = ["id", "title", "order", "count"]
        extra_kwargs = {
            "id": { "read_only": True}, # 仅序列化
            "count": {"write_only": True} # 仅校验
        }
class DpView(APIView):
    authentication_classes = []
    # 同时 序列化 + 校验
    def post(self, request, *args, **kwargs):
        ser = DpSerializer(data=request.data)
        if ser.is_valid():
            instance =  ser.save()
            print(instance, type(instance))
            cc =  DpSerializer(instance=instance)
            return Response(cc.data)
        else:
            return Response("错误")



