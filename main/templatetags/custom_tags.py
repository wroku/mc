from django import template
register = template.Library()


@register.filter
def instance_slug(instance):
    return instance.recipe_slug
