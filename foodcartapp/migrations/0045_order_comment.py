# Generated by Django 4.2.20 on 2025-05-17 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, max_length=250, verbose_name='Комментарий'),
        ),
    ]
