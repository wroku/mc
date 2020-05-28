from django.contrib import admin
from .models import Ingredient, Recipe, Percentage
from django.db import models
# Register your models here.


class IngredientAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Name/category', {'fields': ['ingredient_name', 'ingredient_category']}),
        ('Important Values', {'fields': ['ingredient_price', 'ingredient_calval',
                                         'total_carbs', 'total_fat', 'total_proteins']}),
        ('Underlying magic', {'fields': ['ingredient_slug', "ingredient_image_src"]}),
    ]


class PercentageInline(admin.TabularInline):
    model = Percentage
    extra = 2


class RecipeAdmin(admin.ModelAdmin):

    fields = ('user', 'recipe_name', 'required_spices', 'directions')
    inlines = (PercentageInline,)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
