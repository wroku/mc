from django import template
from main.models import Ingredient

register = template.Library()


@register.filter
def to_str(bound_field):
    # Retrieve Ingredient instance name
    instance = bound_field.cleaned_data
    return instance.ingredient_name
