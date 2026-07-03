import datetime

from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response

from day02 import models
from rest_framework import serializers

class UserInfoSerializer(serializers.ModelSerializer):
    # 自定义字段
    # gender_text = serializers.CharField(source="get_gender_display")
    title = serializers.CharField()
    order = serializers.IntegerField()


    class Meta:
        model = models.Depart
        fields = [ "title", "order"]

class UserView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        # models.UserInfo.objects.all().update(ctime=datetime.datetime.now())
        # 1.获取数据
        queryset = models.Depart.objects.all()
        # 2.序列化
        ser_data = UserInfoSerializer(instance=queryset, many=True)
        # print(ser_data)
        # 3.返回
        context = {"status": True, "data": ser_data.data}
        return Response(context)
        # return  Response('xxx')

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
