# Generated by Django 5.1.4 on 2024-12-08 08:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_post_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='avatar',
        ),
    ]
