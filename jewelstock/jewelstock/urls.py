from django.urls import path
from . import views

app_name = 'jewelstock'
urlpatterns = [
    path('', views.index, name='index'),

    # 在庫管理
    path('stock', views.stock_view, name='stock'),
    path('stock/<int:pk>', views.stock_detail_view, name='stock_detail'),
    path('stock/create', views.stock_create_view, name='stock_create'),
    path('stock/<int:pk>/edit', views.product_edit_view, name='stock_edit'),
    path('stock/<int:pk>/delete', views.stock_delete_view, name='stock_delete'),
    path('stock/existence/<int:pk>', views.stock_existence_view, name='stock_existence'),
    path('stock/create_qr/<int:pk>', views.create_qr, name='create_qr'),

    # 工程管理
    path('progress', views.progress_view, name='progress'),
    path('progress/<int:pk>/delete', views.progress_delete_view, name='progress_delete'),

    # 商品管理
    path('product', views.products_view, name='product'),
    path('product/<int:pk>', views.product_detail_view, name='product_detail'),
    path('product/create', views.product_create_view, name='product_create'),
    path('product/<int:pk>/edit', views.product_edit_view, name='product_edit'),
    path('product/<int:pk>/delete', views.product_delete_view, name='product_delete'),
]
