# Generated by Django 4.1.1 on 2022-10-09 11:41

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_friendrequest_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='profile_image',
            field=models.ImageField(blank=True, default=account.models.get_default_profile_image, null=True, upload_to=account.models.file_up_load, verbose_name='Фотография'),
        ),
    ]
