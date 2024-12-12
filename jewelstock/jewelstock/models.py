from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.safestring import mark_safe
from django.db.models import Q

########################################################
# 1. 組織
########################################################

# j101: 作業所
class Workplace(models.Model):
    name = models.CharField(verbose_name='作業所名', max_length=50)
    address = models.CharField(verbose_name='所在地', max_length=200)
    phone_number_regex = RegexValidator(regex=r'^[0-9]{10,11}$')
    phone_number = models.CharField(verbose_name='電話番号', max_length=11, validators=[phone_number_regex])

    def __str__(self):
        return self.name
    
    def get_progresses(self):
        return Progress.objects.filter(process__workplace=self)

# aj01: 所属
class Assignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='ユーザー', on_delete=models.CASCADE)
    workplace = models.ForeignKey(Workplace, verbose_name='作業所', on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.user.username} -> {self.workplace.name}'

# j102: 取引先
class Company(models.Model):
    name = models.CharField(verbose_name='会社名', max_length=50)
    address = models.CharField(verbose_name='所在地', max_length=200)
    phone_number_regex = RegexValidator(regex=r'^[0-9]{10,11}$')
    phone_number = models.CharField(verbose_name='電話番号', max_length=11, validators=[phone_number_regex])

    def __str__(self):
        return self.name

########################################################
# 2. 型番
########################################################

# j201: 形状
class Shape(models.Model):
    name = models.CharField(verbose_name='形状名', max_length=20)
    def __str__(self):
        return self.name
    
# j202: 型番
class ModelNumber(models.Model):
    model_number_id_regex = RegexValidator(regex=r'^[0-9]{5}$')
    model_number_id = models.PositiveIntegerField(verbose_name='型番', primary_key=True, validators=[model_number_id_regex])
    name = models.CharField(verbose_name='形状名', max_length=20)
    shape = models.ForeignKey(Shape, verbose_name='形状', on_delete=models.PROTECT)

    def __str__(self):
        str = f'[{self.shape}] {self.model_number_id} : {self.name}'
        return str

########################################################
# 3. 製品
########################################################
# j301: カテゴリグループ
class CategoryGroup(models.Model):
    name = models.CharField(verbose_name='カテゴリーグループ', max_length=20)

    def __str__(self):
        return self.name

# j302: カテゴリ
class Category(models.Model):
    name = models.CharField(verbose_name='カテゴリー', max_length=20)
    group = models.ForeignKey(CategoryGroup, verbose_name='グループ', on_delete=models.PROTECT)

    def __str__(self):
        return self.name

# j303: 製品
class Product(models.Model):
    product_code_regex = RegexValidator(regex=r'^[0-9]{14}$')
    product_code = models.PositiveIntegerField(verbose_name='商品コード', primary_key=True, validators=[product_code_regex])
    name = models.CharField(verbose_name='商品名', max_length=200)
    model_number = models.ForeignKey(ModelNumber, verbose_name='形状', on_delete=models.PROTECT)
    category = models.ManyToManyField(Category, verbose_name='カテゴリー', blank=True)
    description = models.CharField(verbose_name='商品説明', max_length=400)
    weight = models.CharField(verbose_name='重量', max_length=200, null=True, blank=True)
    size = models.CharField(verbose_name='サイズ', max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_categories_str(self):
        return "\n".join([category.name for category in self.category.all()])

    def get_categories_obj(self):
        return self.category_set.all()
    
    def count_item(self):
        return Item.objects.filter(product=self).count()
    
# j304: 商品画像
def get_photos_path(instance, filename):
    return "jewelstock/product/%s/image/%s"%(str(instance.product.pk), filename)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name='画像',  upload_to=get_photos_path)

    def image_view(self, obj):
        return mark_safe('<img src="{}" style="width:100px height:auto;">'.format(obj.image.url))


########################################################
# 4. 素材
########################################################

# j401: 材料
class Material(models.Model):
    supplier = models.ForeignKey(Company, verbose_name='仕入れ先', on_delete=models.PROTECT)
    name = models.CharField(verbose_name='材料名', max_length=100)
    stock = models.PositiveIntegerField(verbose_name='在庫数')
    unit = models.CharField(verbose_name='単位', max_length=10)

    def __str__(self):
        return self.name

########################################################
# 5. 単品
########################################################

# j501: アイテム
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

# j502: 材料-アイテムの中間テーブル
class ItemMaterial(models.Model):
    item = models.ForeignKey(Item, verbose_name='単品', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name='材料', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='個数')

# j503: 店頭確認の履歴テーブル
class ItemExistence(models.Model):
    item = models.ForeignKey(Item, verbose_name='単品', on_delete=models.CASCADE)
    existence = models.BooleanField(verbose_name='店頭確認', default=False)
    confirmed_date = models.DateTimeField(verbose_name='確認日時', auto_now_add=True)

########################################################
# 6. 製造工程
########################################################
# j601: 工程
class Process(models.Model):
    operation = models.CharField(verbose_name='作業', max_length=200)
    workplace = models.ForeignKey(Workplace, verbose_name='作業所', on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.workplace}:{self.operation}'
    
# j602: 進捗
class Progress(models.Model):
    item = models.ForeignKey(Item, verbose_name='単品', on_delete=models.CASCADE)
    process = models.ForeignKey(Process, verbose_name='工程', on_delete=models.CASCADE)
    start_date = models.DateTimeField(verbose_name='開始日', null=True, blank=True, default=None)
    due_date = models.DateTimeField(verbose_name='期限', null=True, blank=True, default=None)
    end_date = models.DateTimeField(verbose_name='終了日', null=True, blank=True, default=None)
    confirmor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="確認者", on_delete=models.SET('削除されたユーザー'), null=True, blank=True, default=None)

########################################################
# 7. 発注
########################################################
# j701: 発注
class Order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ordered_material = models.CharField(verbose_name='注文材料', max_length=500)
    workplace = models.ForeignKey(Workplace, verbose_name='発注場所', on_delete=models.PROTECT)
    order_date = models.DateTimeField(verbose_name='発注日時', auto_now_add=True)
    delivery_date = models.DateTimeField(verbose_name='納品日', null=True, blank=True, default=None)

########################################################
# 8. 伝票
########################################################
# j801: 取引形態
class TransactionFormat(models.Model):
    name = models.CharField(verbose_name='取引形態', max_length=10)

    def __str__(self):
        return self.name

# j802: 価格
class Price(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    format = models.ForeignKey(TransactionFormat, verbose_name='販売形態', on_delete=models.CASCADE)
    value = models.PositiveIntegerField(verbose_name='価格')
    start_date = models.DateField(verbose_name='開始日')
    end_date = models.DateField(verbose_name='終了日')

# j803: 伝票
class Voucher(models.Model):
    items = models.ManyToManyField(Item, verbose_name='単品', through='VoucherItem')
    format = models.ForeignKey(TransactionFormat, verbose_name='販売形態', on_delete=models.CASCADE)
    created_date = models.DateField(verbose_name='作成日')
    user_name = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="確認者", on_delete=models.SET('削除されたユーザー'), null=True, blank=True, default=None)
    workplace = models.ForeignKey(Workplace, verbose_name='販売店', on_delete=models.CASCADE)
    memo = models.CharField(verbose_name='備考', max_length=500)
    customer = models.ForeignKey(Company, verbose_name='取引先', on_delete=models.PROTECT)
    transaction_date = models.DateField(verbose_name='取引日')

# j804: 単品価格-伝票の中間テーブル
class VoucherItem(models.Model):
    item = models.ForeignKey(Item, verbose_name='単品', on_delete=models.CASCADE)
    material = models.ForeignKey(Voucher, verbose_name='伝票', on_delete=models.CASCADE)