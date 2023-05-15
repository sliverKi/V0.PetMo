# Generated by Django 4.2 on 2023-05-15 12:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_email_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, error_messages={'unique': '이미 사용중인 닉네임 입니다.'}, max_length=255, unique=True, validators=[django.core.validators.MinLengthValidator(2, '닉네임은 2자 이상이어야 합니다.')], verbose_name='username'),
        ),
    ]
