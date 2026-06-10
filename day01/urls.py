from django.urls import path
from day01 import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'day01'
urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('user/', views.UserView.as_view()),
    path('order/', views.OrderView.as_view()),
    path('avatar/', views.AvatarView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)