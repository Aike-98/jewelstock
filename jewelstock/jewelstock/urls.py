from django.urls import path
from . import views

app_name = 'jewelstock'
urlpatterns = [
    path('', views.index, name='index'),
    path('stock', views.stock_view, name='stock'),
    path('stock/<int:pk>', views.stock_detail_view, name='stock_detail'),
    path('stock/existence/<int:pk>', views.stock_existence_view, name='stock_existence'),
    path('progress', views.progress_view, name='progress'),

    # 商品管理
    path('products', views.products_view, name='products'),
    path('products/create', views.product_create_view, name='products_create'),

    path('stock/create_qr/<int:pk>', views.create_qr, name='create_qr'),
]
