from .models import FoodCategory

def broadcaster(request):
    kwargs = {
        'foodcategories': FoodCategory.objects.all(),
        'currentuser': request.user,

    }
    return kwargs