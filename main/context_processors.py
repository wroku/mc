from .models import FoodCategory

def broadcaster(request):
    kwargs = {
        'foodcategories': FoodCategory.objects.all()
    }
    return kwargs