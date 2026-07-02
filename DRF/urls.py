"""DRF URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin

from django.urls import path, include
from rest_framework import routers

# 创建子路由
router = routers.DefaultRouter()
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('day01/', include('day01.urls', namespace='day01')),
    path('day02/', include('day02.urls', namespace='day02')),
    path('day03/', include('day03.urls', namespace='day03')),
    # path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
    # path('', include('snippets.urls', namespace='Snippets')),
    path('', include('threatbook.urls', namespace='threatbook')),
]

