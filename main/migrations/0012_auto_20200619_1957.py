# Generated by Django 3.0.6 on 2020-06-19 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20200619_1947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='recipe_posted',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date published'),
        ),
    ]
