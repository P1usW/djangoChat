# Generated by Django 4.1.1 on 2022-10-15 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_account_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendrequest',
            name='receiver',
        ),
        migrations.RemoveField(
            model_name='friendrequest',
            name='sender',
        ),
        migrations.DeleteModel(
            name='FriendList',
        ),
        migrations.DeleteModel(
            name='FriendRequest',
        ),
    ]
