# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = 'threatbook'

urlpatterns = [
    path('threatbook/ip/reputation', views.ip_reputation, name='ip_reputation'),
    path('threatbook/mock/ip_reputation', views.mock_ip_reputation, name='mock_ip_reputation'),
]
