from django.contrib import admin
from .models import Ingredient, Recipe, Quantity, FoodCategory
from django.db import models
# Register your models here.


class IngredientAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Name/category', {'fields': ['ingredient_name', 'ingredient_category']}),
        ('Important Values', {'fields': ['ingredient_price', 'ingredient_calval',
                                         'total_carbs', 'total_fat', 'total_proteins']}),
        ('Underlying magic', {'fields': ['ingredient_slug', "ingredient_image_src"]}),
    ]
class FoodCategoryAdmin(admin.ModelAdmin):
    fields = ('category_name', 'category_slug', 'category_image_src', 'category_description')

class QuantityInline(admin.TabularInline):
    model = Quantity
    extra = 2


class RecipeAdmin(admin.ModelAdmin):

    prepopulated_fields = {'recipe_slug': ('recipe_name',)}
    fields = ('user', 'recipe_name', 'recipe_image', 'height_field', 'width_field', 'recipe_slug', 'preparation_time',
              'calories_per_serving' ,'directions')
    inlines = (QuantityInline,)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FoodCategory, FoodCategoryAdmin)
