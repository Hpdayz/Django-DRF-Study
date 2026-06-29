from django.urls import path
from . import  views
from rest_framework.urlpatterns import format_suffix_patterns
app_name = 'day02'
urlpatterns = [
    path('<str:xx>/home/', views.HomeView.as_view(), name='home'),
    path('<str:xx>/depart/',views.DepartView.as_view(), name='depart' )
]

# urlpatterns = format_suffix_patterns(urlpatterns)