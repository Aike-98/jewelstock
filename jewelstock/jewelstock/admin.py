from django.contrib import admin
from .models import *

########################################################
# 1. 組織
########################################################
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone_number')

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'workplace')

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone_number')

admin.site.register(Workplace, WorkplaceAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Company, CompanyAdmin)

########################################################
# 2. 型番
########################################################
class ShapeAdmin(admin.ModelAdmin):
    list_display = ('name', )

class ModelNumberAdmin(admin.ModelAdmin):
    list_display = ('model_number_id', 'shape')

admin.site.register(Shape, ShapeAdmin)
admin.site.register(ModelNumber, ModelNumberAdmin)

########################################################
# 3. 製品
########################################################
class CategoryGroupAdmin(admin.ModelAdmin):
    list_display = ('name', )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'model_number', 'get_categories_str', 'description')

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_view')

admin.site.register(CategoryGroup, CategoryGroupAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductImage, ProductImageAdmin)

########################################################
# 4. 素材
########################################################
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier', 'stock', 'unit')

admin.site.register(Material, MaterialAdmin)

########################################################
# 5. 単品
########################################################
class ItemMaterialAdmin(admin.ModelAdmin):
    list_display = ('item', 'material', 'quantity')

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'product_date', 'sold_date', 'get_materials_by_item')

class ItemExistenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'existence', 'confirmed_date')

admin.site.register(Item, ItemAdmin)
admin.site.register(ItemExistence, ItemExistenceAdmin)

########################################################
# 6. 製造工程
########################################################
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('operation', 'workplace')

class ProgressAdmin(admin.ModelAdmin):
    list_display = ('item', 'process', 'start_date', 'due_date', 'end_date', 'confirmor')

admin.site.register(Process, ProcessAdmin)
admin.site.register(Progress, ProgressAdmin)

########################################################
# 7. 発注
########################################################
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'ordered_material', 'workplace', 'order_date', 'delivery_date')

admin.site.register(Order, OrderAdmin)

########################################################
# 8. 伝票
########################################################
class TransactionFormatAdmin(admin.ModelAdmin):
    list_display = ('name', )

class PriceAdmin(admin.ModelAdmin):
    list_display = ('item', 'value', 'format')

    #TODO: listdisplayに必要なフィールドを追加する

class VoucherAdmin(admin.ModelAdmin):
    list_display = ('format', 'created_date', 'user_name')

admin.site.register(TransactionFormat, TransactionFormatAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Voucher, VoucherAdmin)





