from django.shortcuts import render, redirect
from django.views import View
from .models import *
from .forms import *
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
import os
import pyqrcode
from django.urls import reverse

class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'jewelstock/index.html')

index = IndexView.as_view()

# =======================================
# 在庫管理
# =======================================

# 一覧
class StockView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        query = Q()

        # 検索キーワードを取得し、クエリセットに追加
        keyword = request.GET.get('keyword')
        workplace = request.GET.get('workplace')
        process = request.GET.get('process')
        
        if keyword:
            words = keyword.replace('　', ' ').split(' ')

            for word in words:
                if word == '':
                    continue
                query &= Q(product__name__icontains=word)

        if workplace:
                query &= Q(progress__process__workplace=workplace)

        if process:
                query &= Q(progress__process__operation=process)
        

        # 売却済みのアイテムを除外
        query &= Q(sold_date=None)

        # contextの生成
        items = Item.objects.filter(query)
        products = Product.objects.all()
        workplaces = Workplace.objects.all()
        processes = Process.objects.all()
        
        context['items'] = items
        context['products'] = products
        context['workplaces'] = workplaces
        context['processes'] = processes

        return render(request, 'jewelstock/stock.html', context)
    
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        return redirect('jewelstock:stock')

stock_view = StockView.as_view()

# 詳細
class StockDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        context = {}
        context['item'] = Item.objects.get(pk=pk)
        return render(request, 'jewelstock/stock_detail.html', context)

stock_detail_view = StockDetailView.as_view()


# QR生成
def create_qr(request, pk):
    url = request._current_scheme_host + reverse('jewelstock:stock_existence', args=[pk])
    filepath = f'static/jewelstock/qr/test-item-{pk}.png'
    code = pyqrcode.create(url, error='L', version=5, mode='binary')
    code.png(filepath, scale=5, module_color=[0, 0, 0, 128], background=[255, 255, 255])
    messages.success(request, 'QRコードを生成しました')
    return redirect('jewelstock:stock_detail', pk=pk)


# 店頭確認
class StockExistenceView(View):
    def get(self, request, pk, *args, **kwargs):
        # ログインしていない場合、顧客向けページを表示
        if not request.user.is_authenticated:
            context = {}
            context['product'] = Item.objects.get(pk=pk).product
            return render(request, 'jewelstock/opened_products.html', context)
        
        # ログイン済みの場合、店頭確認ページを表示
        context = {}
        context['item'] = Item.objects.get(pk=pk)
        return render(request, 'jewelstock/stock_existence.html', context)
    
    def post(self, request, *args, **kwargs):
        # ログインしていない場合、顧客向けページへリダイレクト
        if not request.user.is_authenticated:
            return
        
        # ログイン済みの場合、店頭確認の状況を記録
        item_id = request.POST.get('item_id')

        data = {}
        data['item'] = Item.objects.get(pk=item_id)
        data['existence'] = True

        print(f'data:{data}')
        form = ItemExistenceForm(data)

        if form.is_valid():
            # バリデーションOK
            print(f'店頭確認完了:{item_id}')
            form.save()
            messages.success(request, '店頭確認しました')
            return redirect('jewelstock:stock_detail', pk=item_id)
        
        else:
            # バリデーションNG

            # エラーメッセージ
            values = form.errors.get_json_data().values()
            for value in values:
                for v in value:
                    messages.error(request, v["message"])

            return redirect('jewelstock:stock_detail', pk=item_id)

stock_existence_view = StockExistenceView.as_view()



# =======================================
# 発注管理
# =======================================
# =======================================
# 工程管理
# =======================================
class ProgressView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        search_id = request.GET.get('search_id')

        context['workplaces_all'] = Workplace.objects.all()

        if search_id:
            context['workplaces'] = Workplace.objects.filter(pk=search_id)
        else:
            context['workplaces'] = context['workplaces_all']

        return render(request, 'jewelstock/progress.html', context)

progress_view = ProgressView.as_view()


# =======================================
# 商品管理
# =======================================

# 商品一覧
class ProductsView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['products'] = Product.objects.all()
        return render(request, 'jewelstock/products/list.html', context)

products_view = ProductsView.as_view()

# 商品新規作成
class ProductCreateView(View):
    def get(self, request, *args, **kwargs):
        form = ProductForm()
        context = {}
        context['form'] = form
        context['categories'] = ProductCategory.objects.all()
        return render(request, 'jewelstock/products/create_form.html', context)

    def post(self, request, *args, **kwargs):
        print(request.POST)

        categories = request.POST.getlist('categories')
        form = ProductForm(request.POST)

        if form.is_valid():
            # バリデーションOK
            new_product = form.save()

            # 新規商品にManytoManyFieldを追加
            for category in categories:
                category_obj = ProductCategory.objects.get_or_create(name=category)[0]
                new_product.category.add(category_obj)

            new_product.save()
            print('商品を新規作成しました。')
            messages.success(request, '商品を新規作成しました')
            return redirect('jewelstock:products')
        
        else:
            # バリデーションNG
            values = form.errors.get_json_data().values()
            print(form)
            for value in values:
                for v in value:
                    print(v)
                    messages.error(request, v["message"])


        return redirect('jewelstock:products')
    
product_create_view = ProductCreateView.as_view()

# 商品詳細
class ProductDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        context = {}
        context['product'] = Product.objects.get(pk=pk)
        return render(request, 'jewelstock/products/detail.html', context)
    
product_detail_view = ProductDetailView.as_view()

# 商品編集
class ProductEditView(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except:
            return redirect('jewelstock:products')
        
        context = {}
        context['product'] = product
        context['categories'] = ProductCategory.objects.all()
        return render(request, 'jewelstock/products/edit.html', context)
    
    def post(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except:
            return redirect('jewelstock:products')
        
        copied = request.POST.copy()
        copied['product_code'] = pk
        form = ProductForm(copied, instance=product)
        categories = request.POST.getlist('categories')

        if form.is_valid():
            # バリデーションOK
            edited_product = form.save()

            # 新規商品にManytoManyFieldを追加
            for category in categories:
                category_obj = ProductCategory.objects.get_or_create(name=category)[0]
                edited_product.category.add(category_obj)

            edited_product.save()
            print('商品を編集しました。')
            messages.success(request, '商品を編集しました')
            return redirect('jewelstock:product_detail', pk=pk)
        
        else:
            # バリデーションNG
            values = form.errors.get_json_data().values()
            print(form)
            for value in values:
                for v in value:
                    print(v)
                    messages.error(request, v["message"])


        return redirect('jewelstock:product_edit', pk=pk)
    
product_edit_view = ProductEditView.as_view()

# 商品削除
class ProductDeleteView(View):
    def post(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except:
            return redirect('jewelstock:products')
        
        product.delete()
        print('商品を削除しました。')
        messages.success(request, '商品を削除しました。')
        return redirect('jewelstock:products')

product_delete_view = ProductDeleteView.as_view()


# 顧客向け商品紹介ページ
class OpenedProductsView(View):
    def get(self, request, pk, *args, **kwargs):
        context = {}
        context['product'] = Item.objects.get(pk=pk).product
        return render(request, 'jewelstock/opened_products.html', context)
