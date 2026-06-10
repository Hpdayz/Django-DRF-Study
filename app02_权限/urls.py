from django.urls import path
from app02_权限 import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'app02'
urlpatterns = [
    path('order/', views.OrderView.as_view()),
    path('avatar/', views.AvatarView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)