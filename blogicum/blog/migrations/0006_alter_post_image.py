# Generated by Django 3.2.16 on 2024-01-21 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20240120_2111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='blog_images', verbose_name='Фото'),
        ),
    ]
