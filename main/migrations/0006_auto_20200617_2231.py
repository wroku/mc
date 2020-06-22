# Generated by Django 3.0.6 on 2020-06-17 20:31

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20200615_2232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodcategory',
            name='category_image_src',
        ),
        migrations.AddField(
            model_name='foodcategory',
            name='category_image',
            field=models.ImageField(blank=True, height_field='height_field', null=True, upload_to='category_images', width_field='width_field'),
        ),
        migrations.AddField(
            model_name='foodcategory',
            name='height_field',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='foodcategory',
            name='width_field',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='quantity',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quantities', to='main.Recipe'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='recipe_posted',
            field=models.DateField(default=datetime.datetime(2020, 6, 17, 22, 31, 42, 271816), verbose_name='date published'),
        ),
    ]