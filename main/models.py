from django.db import models
from django.conf import settings


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

    def __str__(self):
        return self.ingredient_name


class Recipe(models.Model):
    user = models.ForeignKey(User, default=1, null=True, on_delete=models.SET_NULL)
    recipe_name = models.CharField(primary_key=True, unique=True, max_length=255)
    ingredients = models.ManyToManyField(Ingredient, through='Quantity')
    directions = models.TextField()
    #TODO add imagefield

    def __str__(self):
        return self.recipe_name


class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(default=5)
    #def percentage?