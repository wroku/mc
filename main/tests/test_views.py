from django.test import TestCase
from django.urls import reverse
from main.models import Ingredient, FoodCategory, Recipe, Quantity, Comment
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.contrib import auth

# python manage.py test main.tests.test_views
# coverage run --source='.' manage.py test main
# TODO composition over inheritance... use setUpTestData and put all wet code in functions


class HomepageTest(TestCase):

    def test_get_homepage(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/homepage.html')
        # Temporarily accessing chartpage to check coverage
        self.client.get(reverse('main:chart-page'))


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
                                     image='tree.JPG',
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

    def test_get_recipes(self):
        response = self.client.get(reverse('main:recipes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/recipes.html')

    def test_get_recipe_details(self):
        response = self.client.get(reverse('main:recipe-details', kwargs={'slug': self.recipe.recipe_slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/recipe_details.html')

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
    """
    Test custom admin actions.
    """

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

    def test_get_register(self):
        response = self.client.get(reverse('main:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/register.html')

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

    def test_get_login(self):
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/login.html')

    def test_login(self):
        data = {'username': self.username,
                'password': self.password}
        response = self.client.post(reverse('main:login'), data)
        user = auth.get_user(self.client)
        self.assertRedirects(response, '/')
        self.assertTrue(user.is_authenticated)

    def test_get_user_details(self):
        response = self.client.get('/account', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/account_details.html')

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
        self.assertTemplateUsed(response, 'main/access_denied.html')

    def test_logout_next_fallback(self):
        """
        Plain '/logout' request should redirect to homepage. Real usage deals with next parameter.
        """

        response = self.client.get('/logout', follow=True)
        self.assertRedirects(response, '/', status_code=301)


class IngredientTest(BaseViewTest):

    def test_get_ingredients(self):
        response = self.client.get(reverse('main:products'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/products.html')

    def test_get_ingredient_details(self):
        response = self.client.get(reverse('main:product-details', kwargs={'slug': self.ingredient.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/product_details.html')

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
                'total_proteins': 20,
                'total_carbs': 20,
                'total_fat': 20}
        new_ing = Ingredient(**data)
        self.client.post(change_url, data)
        self.assertEqual(new_ing, Ingredient.objects.get(name='new_ing'))

    def test_total_macronutrients_validator(self):
        """
        Attempt to create ingredient with total macronutrients weight exceeding 100g should be
        unsuccessful due to form validator.
        """

        change_url = reverse('main:add-ingredient')
        data = {'name': 'new_ing',
                'category': self.category,
                'price': 10,
                'calval': 10,
                'image': 'tree.JPG',
                'total_proteins': 35,
                'total_carbs': 35,
                'total_fat': 35}
        self.client.post(change_url, data)
        with self.assertRaises(ObjectDoesNotExist):
            Ingredient.objects.get(name='new_ing')

    def test_redirect_to_details(self):
        """
        Create ingredient via post method (real image needed) and check if redirect chain leads to this ingredient's
        details page.
        """

        change_url = reverse('main:add-ingredient')
        img = SimpleUploadedFile('example.jpg',
                                 content=open('/home/wroku/Dev/muconfi/mc/media_cdn/tree.JPG', 'rb').read(),
                                 content_type='image/jpeg')
        data = {'name': 'new_ing',
                'category': self.category,
                'price': 10,
                'calval': 10,
                'image': img,
                'total_proteins': 20,
                'total_carbs': 20,
                'total_fat': 20}

        response = self.client.post(change_url, data, follow=True)

        self.assertRedirects(response,
                             reverse('main:product-details', kwargs={'slug': Ingredient.objects.get(name=data['name']).slug}))


class ContactUsTest(TestCase):
    """
    Test sending email via contact page and check if message's subject contains intended data.
    """

    def test_get_contact_page(self):
        response = self.client.get(reverse('main:contact-page'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('main/contact_form.html', [tmp.name for tmp in response.templates])

    def test_send_email(self):
        data = {'full_name': 'example user',
                'email': 'test@test.com',
                'content': 'very important message',
                'level_of_importance': 34}

        post_url = reverse('main:contact-page')
        self.client.post(post_url, data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(data['full_name'], mail.outbox[0].subject)
        self.assertIn('AnonymousUser', mail.outbox[0].subject)
        self.assertIn(str(data['level_of_importance']), mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].body, data['content'])
        self.assertEqual(mail.outbox[0].from_email, data['email'])


class IngredientListTest(TestCase):
    """
    Test add, delete and clear - actions of ingredients list which can be tested by django client()
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create few new ingredients. Real image file needed for tests entering product details.
        """

        cls.category = FoodCategory(name='Example Cat')
        cls.category.save()
        img = SimpleUploadedFile('example.jpg',
                                 content=open('/home/wroku/Dev/muconfi/mc/media_cdn/tree.JPG', 'rb').read(),
                                 content_type='image/jpeg')
        defaults = {'name': 'Ing',
                    'category': cls.category,
                    'image': img,
                    'price': 10,
                    'calval': 100,
                    'total_carbs': 10,
                    'total_fat': 10,
                    'total_proteins': 10}

        cls.NUMBER_OF_INGREDIENTS = 5
        for i in range(1, cls.NUMBER_OF_INGREDIENTS + 1):
            defaults['name'] = defaults['name'][:3] + str(i)
            ingredient = Ingredient(**defaults)
            ingredient.save()

        cls.ingredient = Ingredient.objects.get(name='Ing1')

    def test_ingredient_list_template_render(self):
        """
        'ingredient_list.html' template shouldn't be rendered before adding ingredient.
        """

        response = self.client.get(reverse('main:products'))
        self.assertTemplateNotUsed(response, 'main/ingredient_list.html')
        response = self.client.post(reverse('main:products'), {'add': 'added', 'ingredient': self.ingredient.name})
        self.assertTemplateUsed(response, 'main/ingredient_list.html')

    def test_list_add(self):
        """
        Add one ingredient to the list and check if it exists in session data and it's passed to the template in response's context.
        """

        response = self.client.post(reverse('main:products'), {'add': 'added', 'ingredient': self.ingredient.name})
        session = self.client.session
        self.assertEqual(session['collect_ing'][0], self.ingredient.name)
        self.assertEqual(len(response.context['added']), 1)
        self.assertIn(self.ingredient.name, response.context['added'])

    def test_multiple_add(self):
        """
        Add multiple ingredients.
        """

        for name in ['Ing' + str(i) for i in range(1, self.NUMBER_OF_INGREDIENTS + 1)]:
            response = self.client.post(reverse('main:products'), {'add': 'added', 'ingredient': name})

        session = self.client.session
        self.assertEqual(len(response.context['added']), self.NUMBER_OF_INGREDIENTS)
        self.assertEqual(len(session['collect_ing']), self.NUMBER_OF_INGREDIENTS)

    def test_list_delete(self):
        """
        Add two ingredients to the list and delete one of them. Check if change is correctly reflected in
        response's context and session data.
        """

        self.client.post(reverse('main:products'), {'add': 'added', 'ingredient': self.ingredient.name})
        response = self.client.post(reverse('main:products'),
                                    {'add': 'added', 'ingredient': Ingredient.objects.get(name="Ing2").name})
        session = self.client.session
        self.assertEqual(len(response.context['added']), 2)
        self.assertEqual(len(session['collect_ing']), 2)

        response = self.client.post(reverse('main:products'),
                                    {'delete': 'deleted', 'ingredient': self.ingredient.name})
        self.assertEqual(len(response.context['added']), 1)
        session = self.client.session
        self.assertEqual(len(session['collect_ing']), 1)
        self.assertIn(Ingredient.objects.get(name="Ing2").name, response.context['added'])
        self.assertNotIn(self.ingredient.name, response.context['added'])
        self.assertEqual(response.context['added'], session['collect_ing'])

    def test_list_clear(self):
        """
        Add two ingredients remove all from the list with "clear all" option.
        """

        for name in ['Ing' + str(i) for i in range(1, self.NUMBER_OF_INGREDIENTS + 1)]:
            response = self.client.post(reverse('main:products'), {'add': 'added', 'ingredient': name})

        self.assertEqual(len(response.context['added']), self.NUMBER_OF_INGREDIENTS)
        self.assertEqual(self.client.session['collect_ing'], response.context['added'])

        response = self.client.post(reverse('main:products'), {'clear': 'cleared'})
        self.assertEqual(len(response.context['added']), 0)
        self.assertEqual(self.client.session['collect_ing'], response.context['added'])

    def test_invalid_ingredient(self):
        """
        Attempt to add or delete ingredient which does not exist should be unsuccessful.
        """

        response = self.client.post(reverse('main:products'), {'add': 'added', 'ingredient': 'INVALID'})
        self.assertEqual(len(response.context['added']), 0)
        self.assertEqual(len(self.client.session['collect_ing']), 0)

    def test_list_persistence(self):
        """
        Check if ingredients list remain unchanged after visiting another url.
        """

        self.client.post(reverse('main:products'), {'add': 'added', 'ingredient': self.ingredient.name})
        self.client.get(reverse('main:homepage'))
        response = self.client.get(reverse('main:products'))

        self.assertIn(self.ingredient.name, response.context['added'])
        self.assertEqual(len(response.context['added']), 1)
        self.assertEqual(self.client.session['collect_ing'], response.context['added'])

    def test_add_delete_from_details(self):
        response = self.client.post(reverse('main:product-details', kwargs={'slug': self.ingredient.slug}),
                                    {'add': 'added'})
        self.assertIn(self.ingredient.name, response.context['added'])
        self.assertEqual(len(response.context['added']), 1)
        self.assertEqual(self.client.session['collect_ing'], response.context['added'])

        response = self.client.post(reverse('main:product-details', kwargs={'slug': self.ingredient.slug}),
                                    {'delete': 'deleted'})
        self.assertNotIn(self.ingredient.name, response.context['added'])
        self.assertEqual(len(response.context['added']), 0)
        self.assertEqual(self.client.session['collect_ing'], response.context['added'])


class BaseRecipeTest(TestCase):
    """
    Basic setup for tests dealing with adding and editing recipes.
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('Necessary Evil', 'test@example.com', 'SomeP5WD-40')
        cls.category = FoodCategory(name='Example Cat')
        cls.category.save()
        cls.img = SimpleUploadedFile('example.jpg',
                                     content=open('/home/wroku/Dev/muconfi/mc/media_cdn/tree.JPG', 'rb').read(),
                                     content_type='image/jpeg')
        defaults = {'name': 'Ing',
                    'category': cls.category,
                    'image': cls.img,
                    'price': 10,
                    'calval': 100,
                    'total_carbs': 10,
                    'total_fat': 10,
                    'total_proteins': 10}

        cls.NUMBER_OF_INGREDIENTS = 5
        for i in range(1, cls.NUMBER_OF_INGREDIENTS + 1):
            defaults['name'] = defaults['name'][:3] + str(i)
            ingredient = Ingredient(**defaults)
            ingredient.save()

        # TODO Understand whats the problem with ing and recipe using the same example image

        cls.imgr = SimpleUploadedFile('example.jpg',
                                      content=open('/home/wroku/Dev/muconfi/mc/media_cdn/tree.JPG', 'rb').read(),
                                      content_type='image/jpeg')

        cls.default_data = {'recipe_name': 'Example Recipe',
                            'recipe_image': cls.imgr,
                            'preparation_time': 55,
                            'servings': 5,
                            'form-TOTAL_FORMS': 2,
                            'form-INITIAL_FORMS': 0,
                            'form-MIN_NUM_FORMS': 0,
                            'form-MAX_NUM_FORMS': 1000,
                            'form-0-ingredient': Ingredient.objects.all()[0].name,
                            'form-0-quantity': 100,
                            'directions': Ingredient.objects.all()[0].name}


class RecipeDetailsPageTest(BaseRecipeTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.recipe = Recipe(recipe_name='Example Recipe', accepted=True, preparation_time=50,
                            recipe_image='tree.JPG', directions='Ing1')
        for i in range(1, cls.NUMBER_OF_INGREDIENTS + 1):
            Quantity(recipe=cls.recipe,
                     ingredient=Ingredient.objects.get(name=f'Ing{i}'),
                     quantity=100).save()
        cls.recipe.save()

    def test_get_recipe_details(self):
        response = self.client.get(reverse('main:recipe-details', kwargs={'slug': self.recipe.recipe_slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/recipe_details.html')

    def test_post_comment(self):
        self.client.force_login(self.user)
        post_url = reverse('main:recipe-details', kwargs={'slug': self.recipe.recipe_slug})
        data = {'content': 'Mniam mniam'}
        self.client.post(post_url, data)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(Comment.objects.all()[0].content, data['content'])


class RecipeAddTest(BaseRecipeTest):

    def test_get_add_recipe_page(self):
        response = self.client.get(reverse('main:add-recipe'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/addrecipe.html')

    def test_add_valid_recipe(self):
        """
        Check if POSTing new recipe with valid data creates instance in database.
        """

        self.client.force_login(self.user)
        response = self.client.post(reverse('main:add-recipe'), self.default_data, follow=True)
        self.assertEqual(response.context['recipe'], Recipe.objects.get(recipe_name='Example Recipe'))
        self.assertRedirects(response, reverse('main:recipe-details',
                                               kwargs={'slug': Recipe.objects.get(recipe_name='Example Recipe').recipe_slug}))

    def test_duplicate_ingredient_validator(self):
        """
        Update default_data with second identical ingredient and try to POST. Recipe should not be created.
        """

        data = dict(self.default_data)
        data.update({'form-1-ingredient': Ingredient.objects.all()[0].name,
                     'form-1-quantity': 100})
        self.client.force_login(self.user)
        self.client.post(reverse('main:add-recipe'), data, follow=True)
        with self.assertRaises(ObjectDoesNotExist):
            Recipe.objects.get(recipe_name='Example Recipe')

    def test_missing_directions_validator(self):
        """
        Modify directions with text which does not contain chosen ingredient's name. Assert that POST with such data is
        unsuccessful.
        """

        data = dict(self.default_data)
        data['directions'] = 'Unrelated text which does not mention chosen ingredients'
        self.client.force_login(self.user)
        self.client.post(reverse('main:add-recipe'), data, follow=True)
        with self.assertRaises(ObjectDoesNotExist):
            Recipe.objects.get(recipe_name='Example Recipe')

    def test_preparation_time_validator(self):
        """
        Modify directions with text which does not contain chosen ingredient's name. Assert that POST with such data is
        unsuccessful.
        """

        data = dict(self.default_data)
        data['preparation_time'] = 999
        self.client.force_login(self.user)
        self.client.post(reverse('main:add-recipe'), data, follow=True)
        with self.assertRaises(ObjectDoesNotExist):
            Recipe.objects.get(recipe_name='Example Recipe')


class RecipeEditTest(BaseRecipeTest):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.recipe = Recipe(recipe_name='Example Recipe', accepted=True, preparation_time=50,
                            recipe_image='tree.JPG', directions='Ing1')
        for i in range(1, cls.NUMBER_OF_INGREDIENTS + 1):
            Quantity(recipe=cls.recipe,
                     ingredient=Ingredient.objects.get(name=f'Ing{i}'),
                     quantity=100).save()
        cls.recipe.save()

    def test_get_edit_recipe(self):
        """
        Check status code and template used logged in as user which posted recipe.
        """

        self.client.force_login(self.user)
        get_url = reverse('main:recipe-edit', kwargs={'slug': self.recipe.recipe_slug})
        response = self.client.get(get_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/addrecipe.html')

    def test_edit_invalid_recipe_404(self):
        get_url = reverse('main:recipe-edit', kwargs={'slug': 'invalid'})
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, 404)

    def test_edit_recipe(self):
        self.client.force_login(self.user)
        change_url = reverse('main:recipe-edit', kwargs={'slug': self.recipe.recipe_slug})
        data = dict(self.default_data)
        change_data = {'form-INITIAL_FORMS': 1,
                       'form-1-ingredient': Ingredient.objects.all()[1].name,
                       'form-1-quantity': 100,
                       'directions': 'Ing1 & ing2'}
        data.update(change_data)
        response = self.client.post(change_url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('main:recipe-details', kwargs={'slug': self.recipe.recipe_slug}))
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.directions, change_data['directions'])
        self.assertTemplateUsed(response, 'main/recipe_details.html')


class SearchRecipesTest(BaseRecipeTest):
    """
    Using search bar from urls different than '/products/' results in search mode targeting recipes.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create few distinct recipes in addition to superclass setup for purpose of testing search method.
        """

        super().setUpTestData()
        for counter in enumerate(('First', 'Second', 'Third'), 1):
            recipe = Recipe(recipe_name=f'{counter[1]} Recipe', accepted=True, preparation_time=50,
                            recipe_image='tree.JPG', directions='Bypassing form validation')
            for i in range(1, counter[0] + 1):
                Quantity(recipe=recipe,
                         ingredient=Ingredient.objects.get(name=f'Ing{i}'),
                         quantity=100).save()
            recipe.save()

    def test_get_search(self):
        """
        Check status code and template used.
        """
        response = self.client.get(reverse('main:search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/recipes.html')

    def test_search_tip(self):
        """
        Attempt to directly access plain '/search' url should result in count value -1 which triggers displaying search
        feature tip in template.
        """

        response = self.client.get(reverse('main:search'))
        self.assertEqual(response.context['count'], -1)

    def test_empty_query_search(self):
        """
        Clicking search button without entering search query should result in all active recipes displayed.
        """

        response = self.client.get(reverse('main:search'), {'q': ''})
        self.assertEqual(len(response.context['recipes']), 3)

    def test_search(self):
        """
        Check if full tittle search yields expected result. 'count' and 'query' in context data should also
        appropriately reflect data to render summarizing message in template.
        """

        query = {'q': 'First Recipe'}
        response = self.client.get(reverse('main:search'), query)
        self.assertEqual(len(response.context['recipes']), 1)
        self.assertIn(Recipe.objects.get(recipe_name='First Recipe'), response.context['recipes'])
        self.assertEqual(response.context['count'], len(response.context['recipes']))
        self.assertEqual(response.context['query'], query['q'])

    def test_search_title_contains(self):
        """
        Search feature should return all recipes containing query string in title (or directions).
        'First' and 'Third' both contain 'ir' string.
        """

        query = {'q': 'ir'}
        response = self.client.get(reverse('main:search'), query)
        self.assertEqual(len(response.context['recipes']), 2)
        self.assertIn(Recipe.objects.get(recipe_name='First Recipe'), response.context['recipes'])
        self.assertIn(Recipe.objects.get(recipe_name='Third Recipe'), response.context['recipes'])

    def test_search_directions_contains(self):
        query = {'q': 'bypassing'}
        response = self.client.get(reverse('main:search'), query)
        self.assertEqual(len(response.context['recipes']), 3)


class SearchIngredientsTest(BaseRecipeTest):
    """
    Using search bar from '/products/' urls results in search feature mode targeting ingredients.
    """

    def test_get_search_ingredients(self):
        """
        Check that empty query search yields full ingredients queryset.
        Status_code and template used should match expectations too.
        """

        response = self.client.get(reverse('main:products'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/products.html')
        self.assertEqual(len(response.context['ingredients']), self.NUMBER_OF_INGREDIENTS)

    def test_search_ingredient(self):
        query = {'q': 'Ing1'}
        response = self.client.get(reverse('main:products'), query)
        self.assertEqual(len(response.context['ingredients']), 1)
        self.assertIn(Ingredient.objects.get(name='Ing1'), response.context['ingredients'])
        self.assertEqual(response.context['count'], 1)
        self.assertEqual(response.context['query'], query['q'])


class SearchByIngredient(BaseRecipeTest):

    @classmethod
    def setUpTestData(cls):
        """
        Create few distinct recipes in addition to superclass setup for purpose of testing search method.
        """

        super().setUpTestData()
        for counter in enumerate(('First', 'Second', 'Third'), 1):
            recipe = Recipe(recipe_name=f'{counter[1]} Recipe', accepted=True, preparation_time=50,
                            recipe_image='tree.JPG', directions='Bypassing form validation')
            for i in range(1, counter[0] + 1):
                Quantity(recipe=recipe,
                         ingredient=Ingredient.objects.get(name=f'Ing{i}'),
                         quantity=100).save()
            recipe.save()

    def test_get_search_by_ing(self):
        get_url = reverse('main:search-by-ingredients')
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/recipes_containing.html')

    def test_search_by_ing_exact_match(self):
        get_url = reverse('main:search-by-ingredients', kwargs={'query': 'Ing1&Ing2&Ing3'})
        response = self.client.get(get_url)
        self.assertEqual(response.context['recipes'][0][2], 1)
        self.assertEqual(response.context['recipes'][0][0][0][0], Recipe.objects.get(recipe_name='Third Recipe'))

    def test_search_by_ing_partial_match(self):
        get_url = reverse('main:search-by-ingredients', kwargs={'query': 'Ing1&Ing2&Ing3'})
        response = self.client.get(get_url)
        self.assertEqual(response.context['recipes'][1][2], 1)
        self.assertEqual(response.context['recipes'][1][0][0][0], Recipe.objects.get(recipe_name='Second Recipe'))

    def test_search_by_ing_subqueries(self):
        """
        There should be 4 distinct queries, one full (Ing1, Ing2, Ing3) and 3 shorter combinations (with 2 elements).
        """

        get_url = reverse('main:search-by-ingredients', kwargs={'query': 'Ing1&Ing2&Ing3'})
        response = self.client.get(get_url)
        self.assertEqual(len(response.context['recipes']), 4)

    def test_search_by_ing_missing(self):
        """
        Search results should list additional ingredients needed for recipe (which wasn't mentioned in query)
        Second recipe matches query and does not have additional ingredients while third recipe uses also Ing3.
        """

        get_url = reverse('main:search-by-ingredients', kwargs={'query': 'Ing1&Ing2'})
        response = self.client.get(get_url)

        self.assertEqual(response.context['recipes'][0][0][0][0], Recipe.objects.get(recipe_name='Second Recipe'))
        self.assertEqual(response.context['recipes'][0][0][0][1], [])

        self.assertEqual(response.context['recipes'][0][0][1][0], Recipe.objects.get(recipe_name='Third Recipe'))
        self.assertEqual(response.context['recipes'][0][0][1][1][0], Ingredient.objects.get(name='Ing3'))
