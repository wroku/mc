from django import template
from main.models import Ingredient, Recipe
from django.shortcuts import get_object_or_404
register = template.Library()


@register.filter
def to_str(bound_field):
    # Retrieve Ingredient instance name
    instance = bound_field.cleaned_data
    return instance.ingredient_name


@register.filter
def instance_slug(instance):
    return instance.recipe_slug
