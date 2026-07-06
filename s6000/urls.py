from django.urls import path

from . import views

app_name = 's6000'

urlpatterns = [
    path('s6000/intelligence', views.intelligence, name='intelligence'),
]
