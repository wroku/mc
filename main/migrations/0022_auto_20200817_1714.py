# Generated by Django 3.0.9 on 2020-08-17 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20200812_1140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodcategory',
            name='description',
        ),
        migrations.RemoveField(
            model_name='foodcategory',
            name='height_field',
        ),
        migrations.RemoveField(
            model_name='foodcategory',
            name='image',
        ),
        migrations.RemoveField(
            model_name='foodcategory',
            name='width_field',
        ),
    ]
