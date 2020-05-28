# Generated by Django 3.0.6 on 2020-05-28 16:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodCategory',
            fields=[
                ('category_name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('category_slug', models.CharField(max_length=255, unique=True)),
                ('category_image_src', models.CharField(default='main/REPLACE.jpg', max_length=255)),
                ('category_description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('ingredient_name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('ingredient_price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('ingredient_calval', models.IntegerField()),
                ('total_carbs', models.FloatField(default=10)),
                ('total_fat', models.FloatField()),
                ('total_proteins', models.FloatField()),
                ('ingredient_image_src', models.CharField(default='main/REPLACE.jpg', max_length=255)),
                ('ingredient_slug', models.CharField(max_length=255, unique=True)),
                ('ingredient_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.FoodCategory')),
            ],
        ),
        migrations.CreateModel(
            name='Percentage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.FloatField(default=5)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe_name', models.CharField(max_length=255)),
                ('required_spices', models.TextField()),
                ('directions', models.TextField()),
                ('ingredients', models.ManyToManyField(through='main.Percentage', to='main.Ingredient')),
                ('user', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='percentage',
            name='mix',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Recipe'),
        ),
    ]
