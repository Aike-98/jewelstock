from django.contrib import admin
from .models import *

class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone_number')

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'workplace')

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone_number')

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'get_categories_by_product', 'description', 'price')

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_view')

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'stock', 'unit')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'product_date', 'sold_date', 'get_materials_by_item')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'ordered_material', 'workplace', 'order_date', 'delivery_date')

class ProcessAdmin(admin.ModelAdmin):
    list_display = ('operation', 'workplace')

class ProgressAdmin(admin.ModelAdmin):
    list_display = ('item', 'process', 'start_date', 'due_date', 'end_date', 'confirmor')



admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Progress, ProgressAdmin)