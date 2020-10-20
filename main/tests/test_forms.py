from django.test import TestCase
from main.forms import IngredientForm
from main.models import Ingredient, FoodCategory, Recipe, Quantity, Comment


class IngredientFormTest(TestCase):

    def setUp(self):
        self.category = FoodCategory(name='Example Cat')
        self.category.save()

    def test_macronutrients_validator(self):
        """
        Ingredient model custom clean() method should raise ValidationError when sum(total_*) > 100
        """
        data = {'name': 'new_ing',
                'category': self.category,
                'price': 10,
                'calval': 10,
                'image': 'tree.JPG',
                'total_proteins': 35,
                'total_carbs': 35,
                'total_fat': 35}

        form = IngredientForm(data=data)
        self.assertFalse(form.is_valid())