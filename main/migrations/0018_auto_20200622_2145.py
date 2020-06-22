# Generated by Django 3.0.6 on 2020-06-22 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20200622_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='height_field',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='image',
            field=models.ImageField(blank=True, height_field='height_field', null=True, upload_to='ingredient_images', width_field='width_field'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='width_field',
            field=models.IntegerField(default=0),
        ),
    ]
