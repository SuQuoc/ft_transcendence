# Generated by Django 5.0.7 on 2024-07-23 09:40

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_customuser_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_id',
            field=models.UUIDField(editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
