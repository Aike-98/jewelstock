from django.urls import path
from . import views

app_name = 'jewelstock'
urlpatterns = [
    path('', views.index, name='index'),
    path('stock', views.stock_view, name='stock'),
    path('stock/<int:pk>', views.stock_detail_view, name='stock_detail'),
    path('progress', views.progress_view, name='progress'),
    path('products', views.products_view, name='products'),
]
