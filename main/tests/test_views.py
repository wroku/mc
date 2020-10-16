from django.test import TestCase
from django.urls import reverse
from main.models import Ingredient, FoodCategory, Recipe, Quantity, Comment
from django.contrib.auth.models import User
from django.test import Client
from django.contrib import admin

# python manage.py test main.tests.test_views


class SimpleGetTests(TestCase):
    def test_products(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)


class BaseViewTest(TestCase):
    """
    Simple setup for test using objects.
    """

    def setUp(self):
        # Create auth user for views using api request factory
        self.username = 'test_user'
        self.password = 'herewego'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)
        self.client.login(username=self.username, password=self.password)
        # Recipe has to have mock recipe_image attribute which really exists.
        self.recipe = Recipe(recipe_name='Example Recipe', recipe_image='tree.JPG')
        self.recipe.save()

        self.category = FoodCategory(name='Example Cat')
        self.category.save()
        self.ingredient = Ingredient(name='Example Ing',
                                     category=self.category,
                                     price=100,
                                     calval=100,
                                     total_carbs=1,
                                     total_fat=1,
                                     total_proteins=1)
        self.ingredient.save()

        """
        Create two different instances of Recipe to test ordering. This time with assigned quantities to populate 
        (price/calories)_per_serving
        """
        self.recipe2 = Recipe(recipe_name='Example Recipe 2', accepted=True, preparation_time=50, recipe_image='tree.JPG')
        Quantity(recipe=self.recipe2,
                 ingredient=self.ingredient,
                 quantity=100).save()
        self.recipe2.save()

        self.recipe3 = Recipe(recipe_name='Example Recipe 3', accepted=True, preparation_time=40, recipe_image='tree.JPG')
        Quantity(recipe=self.recipe3,
                 ingredient=self.ingredient,
                 quantity=150).save()
        self.recipe3.save()

        self.comment = Comment(recipe=self.recipe, user=User.objects.get(pk=1))
        self.comment.save()


class RecipesViewTest(BaseViewTest):

    def test_recipe_visibility(self):
        """
        Only accepted recipes are visible in view.
        """
        response = self.client.get(reverse('main:recipes'))

        self.assertNotIn(self.recipe, response.context['recipes'])
        self.recipe.accepted = True
        self.recipe.save()

        response = self.client.get(reverse('main:recipes'))
        self.assertIn(self.recipe, response.context['recipes'])

    def test_recipe_ordering(self):
        """
        Make first example recipe visible and test few ordering configurations. Checking only first
        queryset item because of column card fix.
        """
        self.recipe.accepted = True
        self.recipe.save()

        data = {'filter': 'recipe_posted', 'ord': 'asc'}
        response = self.client.get(reverse('main:recipes'), data, follow=True)
        self.assertEqual(response.context['recipes'][0], self.recipe)

        data = {'filter': 'recipe_posted', 'ord': 'desc'}
        response = self.client.get(reverse('main:recipes'), data)
        self.assertEqual(response.context['recipes'][0], self.recipe3)

        data = {'filter': 'calories_per_serving', 'ord': 'desc'}
        response = self.client.get(reverse('main:recipes'), data)
        self.assertEqual(response.context['recipes'][0], self.recipe3)

        data = {'filter': 'price_per_serving', 'ord': 'asc'}
        response = self.client.get(reverse('main:recipes'), data)
        self.assertEqual(response.context['recipes'][0], self.recipe)

        data = {'filter': 'preparation_time', 'ord': 'desc'}
        response = self.client.get(reverse('main:recipes'), data)
        self.assertEqual(response.context['recipes'][0], self.recipe2)


class AdminTests(BaseViewTest):

    def test_approve_recipes(self):
        """
        Perform accepting recipe as logged in superuser.
        """

        data = {'action': 'approve_recipes',
                '_selected_action': [self.recipe.recipe_name,]}
        change_url = reverse('admin:main_recipe_changelist')

        self.assertFalse(self.recipe.accepted)

        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(Recipe.objects.filter(accepted=False, recipe_name__in=data['_selected_action']).count(), 0)

        self.recipe.refresh_from_db()
        self.assertTrue(self.recipe.accepted)
        self.assertEqual(response.status_code, 200)

    def test_approve_ingredient(self):
        data = {'action': 'approve_ingredients',
                '_selected_action': [self.ingredient.name, ]}
        change_url = reverse('admin:main_ingredient_changelist')

        self.assertFalse(self.ingredient.accepted)

        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(Ingredient.objects.filter(accepted=False, name__in=data['_selected_action']).count(), 0)

        self.ingredient.refresh_from_db()
        self.assertTrue(self.ingredient.accepted)
        self.assertEqual(response.status_code, 200)

    def test_approve_comments(self):
        pass

