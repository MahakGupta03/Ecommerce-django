# Generated by Django 4.2.4 on 2023-09-09 13:20

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_product_color_variant_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('coupon_code', models.CharField(max_length=10)),
                ('is_expired', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
