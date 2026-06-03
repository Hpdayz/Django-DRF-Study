from django.urls import path
from app01_认证 import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'app01'

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('app01/user/', views.UserView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)