from django.contrib import admin
from .models import Ingredient, Recipe, Quantity, FoodCategory
from django.db import models
# Register your models here.


class IngredientAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Name/category', {'fields': ['name', 'category']}),
        ('Important Values', {'fields': ['price', 'calval', 'image',
                                         'total_carbs', 'total_fat', 'total_proteins']}),
        ('Underlying magic', {'fields': ['slug', "ingredient_image_src"]}),
    ]


class FoodCategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'image', 'description')


class QuantityInline(admin.TabularInline):
    model = Quantity
    extra = 2


class RecipeAdmin(admin.ModelAdmin):

    prepopulated_fields = {'recipe_slug': ('recipe_name',)}
    fields = ('user', 'recipe_name', 'recipe_image', 'height_field', 'width_field', 'recipe_slug', 'preparation_time',
              'calories_per_serving', 'directions')
    inlines = (QuantityInline,)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FoodCategory, FoodCategoryAdmin)
