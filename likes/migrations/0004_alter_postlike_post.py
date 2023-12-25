# Generated by Django 4.0.10 on 2023-12-25 07:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_initial'),
        ('likes', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postlike',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postLike', to='posts.post'),
        ),
    ]
