# Generated by Django 5.0.7 on 2024-07-30 01:58

import django.db.models.deletion
import jewelstock.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jewelstock', '0004_supplier_process'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='材料名')),
                ('stock', models.PositiveIntegerField(verbose_name='在庫数')),
                ('unit', models.CharField(max_length=10, verbose_name='単位')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='jewelstock.supplier', verbose_name='仕入れ先')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=jewelstock.models.get_photos_path, verbose_name='画像')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jewelstock.product')),
            ],
        ),
    ]
