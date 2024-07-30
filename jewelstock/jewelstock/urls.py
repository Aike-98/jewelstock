from django.urls import path
from . import views

app_name = 'jewelstock'
urlpatterns = [
    path('', views.index, name='index'),
    path('stock', views.stockview, name='stock')
]
