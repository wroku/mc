from django.test import TestCase
from django.urls import reverse
from main.models import Ingredient, FoodCategory, Recipe, Quantity, Comment
from django.contrib.auth.models import User
from django.test import Client
from django.contrib import admin
from main.forms import IngredientForm
from django.core.exceptions import ObjectDoesNotExist

# python manage.py test main.tests.test_views


class SimpleGetTest(TestCase):
    def test_ingredients(self):
        response = self.client.get(reverse('main:products'))
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_recipes(self):
        response = self.client.get(reverse('main:recipes'))
        self.assertEqual(response.status_code, 200)


class BaseViewTest(TestCase):
    """
    Simple  setup for test using objects.
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


class AdminActionsTest(BaseViewTest):

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
        data = {'action': 'approve_comments',
                '_selected_action': [self.comment.id, ]}
        change_url = reverse('admin:main_comment_changelist')

        self.assertFalse(self.comment.active)

        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(Comment.objects.filter(active=False, id__in=data['_selected_action']).count(), 0)

        self.comment.refresh_from_db()
        self.assertTrue(self.comment.active)
        self.assertEqual(response.status_code, 200)


class UserRelatedTest(BaseViewTest):

    def test_register(self):
        """
        Create new user with self.client and check if instance retrieved from database is identical with User created
        by create_user() method.
        """

        new_user = User.objects.create_user(username='new_user', email='brand@new.com', password='Fr3sh&sh1ny')
        change_url = reverse('main:register')
        data = {'username': 'new_user',
                'email': 'brand@new.com',
                'password1': 'Fr3sh&sh1ny',
                'password2': 'Fr3sh&sh1ny'}
        self.client.post(change_url, data)
        self.assertEqual(User.objects.get(username='new_user'), new_user)

    def test_users_details(self):
        """
        /account page should list current user's recipes and comments. Empty querysets are handled
        in template with suitable message.
        """

        response = self.client.get('/account', follow=True)

        self.assertEqual(set(response.context['recipes']), set(Recipe.objects.filter(user=self.user)))
        self.assertEqual(set(response.context['comments']), set(Comment.objects.filter(user=self.user)))
        self.client.logout()

        self.user2 = User.objects.create_user(username='second', email='test@tst.com', password='simpl3P55wd40')
        self.client.login(username='second', password='simpl3P55wd40')
        response = self.client.get('/account', follow=True)
        self.assertEqual(set(response.context['recipes']), set(Recipe.objects.filter(user=self.user2)))
        self.assertEqual(set(response.context['comments']), set(Comment.objects.filter(user=self.user2)))

    def test_access_denied(self):
        """
        Attempt to edit recipe posted by another user should result in redirect to "acces denied" page.
        """

        self.user2 = User.objects.create_user(username='second', email='test@tst.com', password='simpl3P55wd40')
        self.client.logout()
        self.client.login(username='second', password='simpl3P55wd40')
        get_url = reverse('main:recipe-edit', kwargs={'slug': self.recipe.recipe_slug})
        response = self.client.get(get_url, follow=True)
        self.assertRedirects(response, '/access_denied/')

    def test_logout_next_fallback(self):
        """
        Plain '/logout' request should redirect to homepage. Real usage deals with next parameter.
        """

        response = self.client.get('/logout', follow=True)
        self.assertRedirects(response, '/', status_code=301)


class IngredientTest(BaseViewTest):

    def test_recipes_containing(self):
        """
        Supply self.ingredient with example image and check if details page is correctly listing
        recipes with this ingredient
        """

        self.ingredient.image = 'tree.JPG'
        self.ingredient.save()
        get_url = reverse('main:product-details', kwargs={'slug': self.ingredient.slug})
        response = self.client.get(get_url)
        rc_set = {qt.recipe for qt in Quantity.objects.filter(ingredient=self.ingredient)}

        self.assertEqual(set(response.context['recipes_containing']), rc_set)

    def test_add_new_ingredient(self):
        """
        Use form to create new ingredient and check if object fetched from database is identical to
        directly constructed instance.
        """

        change_url = reverse('main:add-ingredient')
        data = {'name': 'new_ing',
                'category': self.category,
                'price': 10,
                'calval': 10,
                'image': 'tree.JPG',
                'total_proteins': 20,
                'total_carbs': 20,
                'total_fat': 20}
        new_ing = Ingredient(**data)
        response = self.client.post(change_url, data)
        self.assertEqual(new_ing, Ingredient.objects.get(name='new_ing'))

    def test_total_macronutrients_validator(self):
        """
        Attempt to create ingredient with total macronutrients weight exceeding 100g should be
        unsuccessful due to form validators.
        """

        change_url = reverse('main:add-ingredient')
        data = {'name': 'new_ing',
                'category': self.category,
                'price': 10,
                'calval': 10,
                'image': 'tree.JPG',
                'total_proteins': 35,
                'total_carbs': 35,
                'total_fat': 35 }
        response = self.client.post(change_url, data)
        with self.assertRaises(ObjectDoesNotExist):
            Ingredient.objects.get(name='new_ing')



