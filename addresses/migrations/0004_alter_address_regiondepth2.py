# Generated by Django 4.0.10 on 2024-01-30 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addresses', '0003_address_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='regionDepth2',
            field=models.CharField(db_index=True, default='', max_length=255),
        ),
    ]