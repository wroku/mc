# Generated by Django 3.0.6 on 2020-06-22 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20200622_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
