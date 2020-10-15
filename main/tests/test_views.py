from django.test import TestCase
from django.urls import reverse
from main.models import Ingredient, FoodCategory, Recipe, Quantity, Comment
from django.contrib.auth.models import User
from django.test import Client


class SimpleTest(TestCase):
    def test_products(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)


class AdminTests(TestCase):

    def setUp(self):
        # Create auth user for views using api request factory
        self.username = 'test_user'
        self.password = 'herewego'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)

        # Create some object to perform the action on
        self.recipe = Recipe(recipe_name='Example Recipe')
        self.recipe.save()

        self.category = FoodCategory(name='Example Cat')
        self.category.save()

        self.comment = Comment(recipe=self.recipe, user=User.objects.get(pk=1))
        self.comment.save()

        self.ingredient = Ingredient(name='Example Ing',
                                     category=self.category,
                                     price=5,
                                     calval=1,
                                     total_carbs=1,
                                     total_fat=1,
                                     total_proteins=1)
        self.ingredient.save()

    def test_approve_recipes(self):
        """
        Login as superuser and perform accepting recipe
        """

        self.client = Client()
        data = {'action': 'approve_recipes',
                '_selected_action': [self.recipe.recipe_name, ]}
        change_url = reverse('admin:main_recipe_changelist')
        self.client.login(username=self.username, password=self.password)

        self.assertFalse(self.recipe.accepted)
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()

        self.assertTrue(self.recipe.accepted)
        self.assertEqual(response.status_code, 200)