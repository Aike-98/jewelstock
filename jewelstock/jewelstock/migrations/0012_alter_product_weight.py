# Generated by Django 5.0.7 on 2024-08-30 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jewelstock', '0011_itemexistence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='重量'),
        ),
    ]