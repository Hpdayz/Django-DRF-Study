from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
# 导入版本组件
from rest_framework.versioning import QueryParameterVersioning, URLPathVersioning
# 导入解析器
from rest_framework.parsers import JSONParser, FormParser
# 导入p
from rest_framework.negotiation import DefaultContentNegotiation
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