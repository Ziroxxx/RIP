# Generated by Django 5.1 on 2024-09-12 14:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('astro', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='requests',
            name='moderID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='moderated_reqs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='requests',
            name='userID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_reqs', to=settings.AUTH_USER_MODEL),
        ),
    ]
