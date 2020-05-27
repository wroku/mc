from django.db import models
from django.conf import settings


# Create your models here.

User = settings.AUTH_USER_MODEL


class Ingredient(models.Model):
    FOOD_CATEGORIES = (
        ('FR', 'Fruits'),
        ('NU', 'Nuts'),
        ('FL', 'Flakes'),
        ('SE', 'Seeds'),
        ('OT', 'Other'),
    )
    ingredient_name = models.CharField(max_length=200, primary_key=True)
    ingredient_price = models.IntegerField()
    ingredient_calval = models.IntegerField()
    total_carbs = models.FloatField(default=10)
    total_fat = models.FloatField()
    total_proteins = models.FloatField()
    ingredient_category = models.CharField(max_length=2, choices=FOOD_CATEGORIES)
    ingredient_image_src = models.CharField(max_length=255, default=f'main/REPLACE.jpg')
    ingredient_slug = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.ingredient_name


class Mix(models.Model):
    user = models.ForeignKey(User, default=1, null=True, on_delete=models.SET_NULL)
    mix_name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(Ingredient, through='Percentage')

    def __str__(self):
        return self.mix_name


class Percentage(models.Model):
    mix = models.ForeignKey(Mix, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    percentage = models.FloatField(default=5)
    #def percentage?