from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import *
from .forms import *
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
import os
import pyqrcode
from django.urls import reverse, resolve

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

        return render(request, 'jewelstock/stock/list.html', context)
    
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        return redirect('jewelstock:stock')

stock_view = StockView.as_view()

# 詳細
class StockDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        context = {}
        context['item'] = Item.objects.get(pk=pk)
        context['processes'] = Process.objects.all()
        return render(request, 'jewelstock/stock/detail.html', context)
    
    # def post(self, request, pk, *args, **kwargs):
    #     item = get_object_or_404(Item, id=pk)
    #     new_progresses = {}
    #     new_progresses['process'] = request.POST.getlist('process')
    #     new_progresses['start_date'] = request.POST.getlist('start_date')
    #     new_progresses['due_date'] = request.POST.getlist('due_date')

    #     print(new_progresses)
    #     for i in range(0, len(new_progresses['process']), 1):
    #         new_progress = {}
    #         new_progress['item'] = item
    #         new_progress['process'] = new_progresses['process'][i]
    #         new_progress['start_date'] = new_progresses['start_date'][i]
    #         new_progress['due_date'] = new_progresses['due_date'][i]

    #         form = ProgressForm(new_progress)

    #         if form.is_valid():
    #             form.save()
    #             messages.success(request, '工程を追加しました')
        
    #         else:
    #             # バリデーションNG
    #             values = form.errors.get_json_data().values()
    #             for value in values:
    #                 for v in value:
    #                     messages.error(request, v["message"])
            

    #     context = {}
    #     context['item'] = item
    #     context['processes'] = Process.objects.all()
    #     return render(request, 'jewelstock/stock/detail.html', context)

stock_detail_view = StockDetailView.as_view()

# 新規作成
class StockCreateView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['products'] = Product.objects.all()
        return render(request, 'jewelstock/stock/create_form.html', context)
    
    def post(self, request, *args, **kwargs):
        product = request.POST.get('product_code')
        item = Item()
        item.product = Product.objects.get(product_code=product)
        item.save()
        return redirect('jewelstock:stock')

stock_create_view = StockCreateView.as_view()

# 削除
class StockDeleteView(View):
    def post(self, request, pk, *args, **kwargs):
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        print('アイテムを削除しました。')
        messages.success(request, 'アイテムを削除しました。')
        return redirect('jewelstock:stock')

stock_delete_view = StockDeleteView.as_view()


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
        return render(request, 'jewelstock/stock/confirm_existence.html', context)
    
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

class ProgressDeleteView(View):
    def post(self, request, pk, *args, **kwargs):
        path = request.POST.get('path')
        print(f'path:{path}')
        print(f'resolverMatch:{resolve(path)}')
        appname = resolve(path).app_name
        urlname = resolve(path).url_name
        id = resolve(path).kwargs['id']
        print(f'urlname:{urlname}')
        progress = get_object_or_404(Progress, pk=pk)    
        progress.delete()
        print('工程を削除しました。')
        messages.success(request, '工程を削除しました。')

        return redirect(appname + ':' + urlname, pk=id)

progress_delete_view = ProgressDeleteView.as_view()

class ProgressCreateView(View):
    def get(self, request, pk, *args, **kwargs):
        return
    
    def post(self, request, pk, *args, **kwargs):
        return

# =======================================
# 商品管理
# =======================================

# 商品一覧
class ProductsView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['products'] = Product.objects.all()
        return render(request, 'jewelstock/product/list.html', context)

products_view = ProductsView.as_view()

# 商品新規作成
class ProductCreateView(View):
    def get(self, request, *args, **kwargs):
        form = ProductForm()
        context = {}
        context['form'] = form
        context['categories'] = ProductCategory.objects.all()
        return render(request, 'jewelstock/product/create_form.html', context)

    def post(self, request, *args, **kwargs):
        print(request.POST)

        form = ProductForm(request.POST)

        # カテゴリの新規作成と取得
        categories = request.POST.getlist('categories')
        category_objs = []
        for category in categories:
            category_obj = ProductCategory.objects.get_or_create(name=category)[0]
            category_objs.append(category_obj)
            

        if form.is_valid():
            # バリデーションOK
            new_product = form.save()

            # 新規商品にManytoManyFieldを追加
            for category in category_objs:
                new_product.category.add(category)
            new_product.save()

            print('商品を新規作成しました。')
            messages.success(request, '商品を新規作成しました')
            return redirect('jewelstock:product')
        
        else:
            # バリデーションNG
            values = form.errors.get_json_data().values()
            print(form)
            for value in values:
                for v in value:
                    print(v)
                    messages.error(request, v["message"])


        return redirect('jewelstock:product')
    
product_create_view = ProductCreateView.as_view()

# 商品詳細
class ProductDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        context = {}
        context['product'] = Product.objects.get(pk=pk)
        return render(request, 'jewelstock/product/detail.html', context)
    
product_detail_view = ProductDetailView.as_view()

# 商品編集
class ProductEditView(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except:
            return redirect('jewelstock:product')
        
        context = {}
        context['product'] = product
        context['categories'] = ProductCategory.objects.all()
        return render(request, 'jewelstock/product/edit.html', context)
    
    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, product_code=pk)    
        
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
        product = get_object_or_404(Product, product_code=pk)    
        product.delete()
        print('商品を削除しました。')
        messages.success(request, '商品を削除しました。')
        return redirect('jewelstock:product')

product_delete_view = ProductDeleteView.as_view()


# 顧客向け商品紹介ページ
class OpenedProductsView(View):
    def get(self, request, pk, *args, **kwargs):
        context = {}
        context['product'] = Item.objects.get(pk=pk).product
        return render(request, 'jewelstock/opened_products.html', context)
