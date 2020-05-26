from django.contrib import admin
from .models import Ingredient, Mix, Percentage
from django.db import models
# Register your models here.

class IngredientAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Name/category', {'fields': ['ingredient_name', 'ingredient_category']}),
        ('Important Values', {'fields': ['ingredient_price', 'ingredient_calval']}),
        ('Underlying magic', {'fields': ['ingredient_slug', "ingredient_image_src"]}),
    ]


admin.site.register(Mix)
admin.site.register(Ingredient, IngredientAdmin)
