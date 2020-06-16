from django.db import models
from django.conf import settings
from datetime import datetime
from django.db.models.signals import pre_save
from django.utils.text import slugify

# Create your models here.

User = settings.AUTH_USER_MODEL


class FoodCategory(models.Model):
    category_name = models.CharField(max_length=255, primary_key=True)
    category_slug = models.CharField(max_length=255, unique=True)
    category_image_src = models.CharField(max_length=255, default=f'main/REPLACE.jpg')
    category_description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name


class Ingredient(models.Model):

    ingredient_name = models.CharField(max_length=255, primary_key=True)
    ingredient_category = models.ForeignKey(FoodCategory, null=True, blank=True, on_delete=models.SET_NULL)

    ingredient_price = models.DecimalField(max_digits=7, decimal_places=2)
    ingredient_calval = models.IntegerField()
    total_carbs = models.FloatField(default=10)
    total_fat = models.FloatField()
    total_proteins = models.FloatField()

    ingredient_image_src = models.CharField(max_length=255, default=f'main/REPLACE.jpg')
    ingredient_slug = models.CharField(max_length=255, unique=True)
    # TODO Change slug to slugfield and set prepopulate

    def __str__(self):
        return self.ingredient_name


def upload_location(recipe, filename):
    return "%s/%s" %(recipe.user, filename)


class Recipe(models.Model):
    user = models.ForeignKey(User, default=1, null=True, on_delete=models.SET_NULL)
    recipe_posted = models.DateField('date published', default=datetime.now())
    recipe_name = models.CharField(primary_key=True, unique=True, max_length=255)
    recipe_slug = models.SlugField(null=True, blank=True, unique=True)

    recipe_image = models.ImageField(upload_to=upload_location,
                                     null=True,
                                     blank=True,
                                     width_field='width_field',
                                     height_field='height_field')
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    ingredients = models.ManyToManyField(Ingredient, through='Quantity')
    directions = models.TextField()
    preparation_time = models.IntegerField(default=45)

    def __str__(self):
        return self.recipe_name


def pre_save_recipe_receiver(sender, instance, *args, **kwargs):
    slug = slugify(instance.recipe_name)
    # Dont have to check if slug exists becouse recipe_name is unique
    instance.recipe_slug = slug


pre_save.connect(pre_save_recipe_receiver, sender=Recipe)


class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(default=5)
