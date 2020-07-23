from django.db import models
from django.conf import settings
from datetime import datetime
from django.db.models.signals import pre_save
from django.utils.text import slugify
from decimal import *
from django.db.models import Q

# Create your models here.
getcontext().prec = 2
User = settings.AUTH_USER_MODEL


class FoodCategory(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images',
                              null=True,
                              blank=True,
                              width_field='width_field',
                              height_field='height_field')
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(max_length=255, primary_key=True)
    category = models.ForeignKey(FoodCategory, null=True, blank=True, on_delete=models.SET_NULL)

    price = models.DecimalField(max_digits=7, decimal_places=2)
    calval = models.IntegerField()
    total_carbs = models.FloatField()
    total_fat = models.FloatField()
    total_proteins = models.FloatField()

    image = models.ImageField(upload_to='ingredient_images',
                              null=True,
                              blank=True,
                              width_field='width_field',
                              height_field='height_field')
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)

    ingredient_image_src = models.CharField(max_length=255, default=f'main/REPLACE.jpg')
    slug = models.SlugField(null=True, blank=True, unique=True)
    # TODO Change slug to slugfield and set prepopulate

    def __str__(self):
        return self.name


def upload_location(recipe, filename):
    return "%s/%s" % (recipe.user, filename)


def pre_save_slugifier(sender, instance, *args, **kwargs):
    slug = slugify(instance.name)
    instance.slug = slug


pre_save.connect(pre_save_slugifier, sender=FoodCategory)
pre_save.connect(pre_save_slugifier, sender=Ingredient)


class RecipeManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookap = (Q(recipe_name__icontains=query) |
                         Q(directions__icontains=query) |
                         Q(recipe_slug__icontains=query)
                         )
            qs = qs.filter(or_lookap).distinct()
        return qs

    def search_by_ing(self, ing=None):
        qs = self.get_queryset()
        if ing:
            qs = ing.recipe_set.all()
        return qs
    # For searching by multiple ingredients maybe chain querysets /combine .distinct(), without next manager method

    def search_by_ings(self, ings=[]):
        qs = self.get_queryset()



class Recipe(models.Model):
    user = models.ForeignKey(User, default=1, null=True, on_delete=models.SET_NULL)
    recipe_posted = models.DateTimeField('date published', auto_now_add=True)
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
    servings = models.IntegerField(default=2)
    # Data replication, I will leave it here for now
    calories_per_serving = models.IntegerField(blank=True, null=True)
    price_per_serving = models.DecimalField(max_digits=7, decimal_places=2)

    objects = RecipeManager()

    def __str__(self):
        return self.recipe_name


def pre_save_recipe_receiver(sender, instance, *args, **kwargs):
    slug = slugify(instance.recipe_name)
    # Don't have to check if slug exists because recipe_name is unique
    instance.recipe_slug = slug
    qs = instance.quantities.all()
    cps, pps = 0, 0
    for q in qs:
        ing = Ingredient.objects.get(name=q.ingredient)
        cps += q.quantity/1000 * ing.calval
        pps += (q.quantity * ing.price)/1000
    instance.calories_per_serving = round(cps/int(instance.servings))
    instance.price_per_serving = round(pps/int(instance.servings), 2)


pre_save.connect(pre_save_recipe_receiver, sender=Recipe)


class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='quantities')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,)
    quantity = models.IntegerField(default=5)

    class Meta:
        verbose_name_plural = 'Quantities'


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=2000)
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
