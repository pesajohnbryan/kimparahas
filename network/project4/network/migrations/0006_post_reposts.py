# Generated by Django 5.1.4 on 2024-12-08 08:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_remove_post_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='reposts',
            field=models.ManyToManyField(blank=True, related_name='reposted_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
