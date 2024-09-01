from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.safestring import mark_safe
from django.db.models import Q

# 作業所
class Workplace(models.Model):
    name = models.CharField(verbose_name='作業所名', max_length=50)
    address = models.CharField(verbose_name='所在地', max_length=200)
    phone_number_regex = RegexValidator(regex=r'^[0-9]{10,11}$')
    phone_number = models.CharField(verbose_name='電話番号', max_length=11, validators=[phone_number_regex])

    def __str__(self):
        return self.name
    
    def get_progresses(self):
        return Progress.objects.filter(process__workplace=self)

# 所属
class Assignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='ユーザー', on_delete=models.CASCADE)
    workplace = models.ForeignKey(Workplace, verbose_name='作業所', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.user.username} -> {self.workplace.name}'

# 仕入れ先
class Supplier(models.Model):
    name = models.CharField(verbose_name='会社名', max_length=50)
    address = models.CharField(verbose_name='所在地', max_length=200)
    phone_number_regex = RegexValidator(regex=r'^[0-9]{10,11}$')
    phone_number = models.CharField(verbose_name='電話番号', max_length=11, validators=[phone_number_regex])

    def __str__(self):
        return self.name

# 商品カテゴリ
class ProductCategory(models.Model):
    name = models.CharField(verbose_name='カテゴリー', max_length=20)

    def __str__(self):
        return self.name

# 商品
class Product(models.Model):
    product_code_regex = RegexValidator(regex=r'^[0-9]{14}$')
    product_code = models.PositiveIntegerField(verbose_name='商品コード', primary_key=True, validators=[product_code_regex])
    name = models.CharField(verbose_name='商品名', max_length=200)
    category = models.ManyToManyField(ProductCategory, verbose_name='カテゴリー', blank=True)
    description = models.CharField(verbose_name='商品説明', max_length=400)
    weight = models.CharField(verbose_name='重量', max_length=200, null=True, blank=True)
    size = models.CharField(verbose_name='サイズ', max_length=200, null=True, blank=True)
    price = models.PositiveIntegerField(verbose_name='税込み価格')

    def __str__(self):
        return self.name
    
    def get_categories_str(self):
        return "\n".join([category.name for category in self.category.all()])

    def get_categories_obj(self):
        return self.category_set.all()
    
# 商品画像
def get_photos_path(instance, filename):
    return "jewelstock/product/%s/image/%s"%(str(instance.product.pk), filename)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='画像',  upload_to=get_photos_path)

    def image_view(self, obj):
        return mark_safe('<img src="{}" style="width:100px height:auto;">'.format(obj.image.url))

# 材料
class Material(models.Model):
    supplier = models.ForeignKey(Supplier, verbose_name='仕入れ先', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='材料名', max_length=100)
    stock = models.PositiveIntegerField(verbose_name='在庫数')
    unit = models.CharField(verbose_name='単位', max_length=10)

    def __str__(self):
        return self.name


# アイテム
class Item(models.Model):
    product = models.ForeignKey(Product, verbose_name='商品', on_delete=models.PROTECT)
    product_date = models.DateField(verbose_name='製造日', null=True, blank=True, default=None)
    sold_date = models.DateField(verbose_name='売却日', null=True, blank=True, default=None)
    item_material = models.ManyToManyField(Material, verbose_name='材料', through='ItemMaterial')

    def __str__(self):
        return f'{self.id}: {self.product.name}'
    
    def get_materials_by_item(self):
        return "\n".join([material.name for material in self.item_material.all()])
    
    def get_now_progresses(self):
        now = timezone.now()
        query = Q()
        query &= Q(item=self)
        query &= Q(start_date__lte=now)
        query &= Q(end_date__isnull=True)
        progresses = Progress.objects.filter(query)
        return progresses
    
    def get_all_progresses(self):
        return Progress.objects.filter(item=self).order_by('start_date').reverse()
    
    def get_now_existence(self):
        now = localtime(timezone.now())
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return ItemExistence.objects.filter(confirmed_date__gte=today, item=self.id)

# 材料-アイテムの中間テーブル
class ItemMaterial(models.Model):
    item = models.ForeignKey(Item, verbose_name='アイテム', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name='材料', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='個数')

# 店頭確認の履歴テーブル
class ItemExistence(models.Model):
    item = models.ForeignKey(Item, verbose_name='アイテム', on_delete=models.CASCADE)
    existence = models.BooleanField(verbose_name='店頭確認', default=False)
    confirmed_date = models.DateTimeField(verbose_name='確認日時', auto_now_add=True)

# 発注
class Order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ordered_material = models.CharField(verbose_name='注文材料', max_length=500)
    workplace = models.ForeignKey(Workplace, verbose_name='発注場所', on_delete=models.PROTECT)
    order_date = models.DateTimeField(verbose_name='発注日時', auto_now_add=True)
    delivery_date = models.DateTimeField(verbose_name='納品日', null=True, blank=True, default=None)

# 工程
class Process(models.Model):
    operation = models.CharField(verbose_name='作業', max_length=200)
    workplace = models.ForeignKey(Workplace, verbose_name='作業所', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.workplace}:{self.operation}'
    
# 進捗
class Progress(models.Model):
    item = models.ForeignKey(Item, verbose_name='アイテム', on_delete=models.CASCADE)
    process = models.ForeignKey(Process, verbose_name='工程', on_delete=models.CASCADE)
    start_date = models.DateTimeField(verbose_name='開始日', null=True, blank=True, default=None)
    due_date = models.DateTimeField(verbose_name='期限', null=True, blank=True, default=None)
    end_date = models.DateTimeField(verbose_name='終了日', null=True, blank=True, default=None)
    confirmor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="確認者", on_delete=models.SET('削除されたユーザー'), null=True, blank=True, default=None)
