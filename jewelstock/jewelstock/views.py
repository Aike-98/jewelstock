from django.shortcuts import render
from django.views import View
from .models import *
from django.db.models import Q

class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'jewelstock/index.html')

index = IndexView.as_view()

# 在庫管理
class StockView(View):
    def get(self, request, *args, **kwargs):
        items = Item.objects.filter(sold_date=None)
        context = {'items' : items}
        return render(request, 'jewelstock/stock.html', context)

stockview = StockView.as_view()

# 発注管理
# 工程管理
# 商品管理