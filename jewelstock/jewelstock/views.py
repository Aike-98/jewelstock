from django.shortcuts import render, redirect
from django.views import View
from .models import *
from django.db.models import Q

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
        
        if keyword:
            words = keyword.replace('　', ' ').split(' ')

            for word in words:
                if word == '':
                    continue
                query &= Q(product__name__icontains=word)

        # 売却済みのアイテムを除外
        query &= Q(sold_date=None)

        # contextの生成
        items = Item.objects.filter(query)
        products = Product.objects.all()
        context['items'] = items
        context['products'] = products

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
        print(context)
        return render(request, 'jewelstock/stock_detail.html', context)

stock_detail_view = StockDetailView.as_view()



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
class ProductsView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['products'] = Product.objects.all()
        return render(request, 'jewelstock/products.html', context)

products_view = ProductsView.as_view()
