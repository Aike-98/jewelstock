from django.urls import path
from . import views

app_name = 'jewelstock'
urlpatterns = [
    path('', views.index, name='index')
]
