# Generated by Django 4.2.4 on 2023-09-01 18:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='register',
            old_name='user_name',
            new_name='email',
        ),
        migrations.RenameField(
            model_name='register',
            old_name='id',
            new_name='uid',
        ),
        migrations.AddField(
            model_name='register',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='register',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
