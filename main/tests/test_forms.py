from django.test import TestCase
from main.forms import IngredientForm, ContactForm
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


class ContactPageFormTest(TestCase):

    def setUp(self):
        self.data = {'full_name': 'example user',
                     'email': 'test@test.com',
                     'content': 'very important message',
                     'level_of_importance': 34}

    def test_valid_message(self):
        form = ContactForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        self.data['email'] = 'invalid_email'
        form = ContactForm(data=self.data)
        self.assertFalse(form.is_valid())
