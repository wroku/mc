from django import template
register = template.Library()


@register.filter
def to_str(bound_field):
    # Retrieve Ingredient instance name
    instance = bound_field.cleaned_data
    return instance.ingredient_name


@register.filter
def instance_slug(instance):
    return instance.recipe_slug
