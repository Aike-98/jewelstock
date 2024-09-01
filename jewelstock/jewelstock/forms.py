from django import forms
from .models import *
from django.utils import timezone
from django.utils.timezone import localtime
from django.core.exceptions import ValidationError

# Productフォーム
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_code', 'name', 'description', 'weight', 'size', 'price']

# 店頭確認
class ItemExistenceForm(forms.ModelForm):
    class Meta:
        model = ItemExistence
        fields = ['item', 'existence']

