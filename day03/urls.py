from django.urls import path
from . import  views
from rest_framework.urlpatterns import format_suffix_patterns
app_name = 'day03'
urlpatterns = [
    path('user/', views.UserView.as_view()),
    path('depart/', views.DepartView.as_view()),
    path('dp/', views.DpView.as_view()),
]

# urlpatterns = format_suffix_patterns(urlpatterns)