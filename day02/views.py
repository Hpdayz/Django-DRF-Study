import datetime

from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
# 导入版本组件
from rest_framework.versioning import QueryParameterVersioning, URLPathVersioning
# 导入解析器
from rest_framework.parsers import JSONParser, FormParser
# 通过请求选择解析器
from rest_framework.negotiation import DefaultContentNegotiation

from day02 import models
from rest_framework import serializers


class DepartSerializer(serializers.Serializer):
    title = serializers.CharField()
    count = serializers.IntegerField()


# class DepartSerializer(serializers.ModelSerializer):
#     # 通过ModelSerializer来简化代码
#     class Meta:
#         model = models.Depart
#         fields = "__all__"



class DepartView(APIView):
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        # 1.从数据库中获取数据 {"id": xx, "title": "xx"}
        # depart_obj = models.Depart.objects.all().first()
        depart_obj = models.Depart.objects.all()
        print(depart_obj)
        # 2.序列化器转换成JSON格式：int/str/list/dict/
        # 如果需要处理的数据是多个，例如[ obj1, obj2, ... ]
        # 可以增加参数 many=True DepartSerializer(instance=depart_obj, many=True)
        ser = DepartSerializer(instance=depart_obj, many=True)
        print(ser.data)
        # 3.返回数据给用户
        context = { "status": 200, "data": ser.data }
        return Response(context)


class D1(serializers.ModelSerializer):
    class Meta:
        model = models.Depart
        fields = "__all__"


class D2(serializers.ModelSerializer):
    class Meta:
        model = models.Tags
        fields = "__all__"


class UserInfoSerializer(serializers.ModelSerializer):
    # 自定义字段
    # gender_text = serializers.CharField(source="get_gender_display")
    # depart_title = serializers.CharField(source="depart.title")
    # ctime = serializers.DateTimeField(format("%Y-%m-%d"))
    # # 创建新字段
    # ccc = serializers.SerializerMethodField()

    # 嵌套
    depart = D1()
    tag = D2(many=True)
    class Meta:
        model = models.UserInfo
        # fields = "__all__"
        # fields = ["name", "age", "gender_text", "depart_title", "ctime", "ccc"]
        fields = ["depart", "tag"]
    # def get_ccc(self, obj):
    #     queryset = obj.tag.all()
    #     res = [{"id": tag.id, "caption": tag.caption} for tag in queryset]
    #     print(queryset)
    #     return res

class UserView(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        # models.UserInfo.objects.all().update(ctime=datetime.datetime.now())
        # 1.获取数据
        queryset = models.UserInfo.objects.all()
        # 2.序列化
        ser_data = UserInfoSerializer(instance=queryset, many=True)
        # print(ser_data)
        # 3.返回
        context = {"status": True, "data": ser_data.data}
        return Response(context)


class HomeView(APIView):
    authentication_classes = []
    # 配置文件 VERSION_PARAM -> 决定路径参数中的变量名
    # http://127.0.0.1:8000/day02/home/?version=v1&user=xxx&age=12
    versioning_class = URLPathVersioning
    # 所有的解析器
    parser_classes = [JSONParser, FormParser]
    # 根据请求头，匹配对应的解析器
    content_negotiation_class = DefaultContentNegotiation

    def get(self,request, *args, **kwargs):
        print(request.version)
        print(request.versioning_scheme)
        url = request.versioning_scheme.reverse("day02:home", request=request)
        print("反向生成的URL：", url)
        self.dispatch
        return Response('HomeView')

    def post(self, request, *args, **kwargs):
        print(request.data, type(request.data))
        return Response("ok")