# -*- coding: utf-8 -*-
from django.urls import path

from . import views

app_name = "s6000"

urlpatterns = [
    path("s6000/intelligence", views.intelligence, name="intelligence"),
    path("s6000/intelligence_gc", views.intelligence_gc, name="intelligence_gc"),
]
