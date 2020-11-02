from django.test import TestCase
from main.forms import IngredientForm, ContactForm, NewUserForm, RecipeForm, RecipeIngredient
from main.models import Ingredient, FoodCategory, Recipe, Quantity, Comment
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


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

    @classmethod
    def setUpTestData(cls):
        cls.data = {'full_name': 'example user',
                    'email': 'test@test.com',
                    'content': 'very important message',
                    'level_of_importance': 34}

    def test_valid_message(self):
        form = ContactForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        data = dict(self.data)
        data['email'] = 'invalid_email'
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())


class UserRegisterFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.data = {'username': 'new_user',
                    'email': 'brand@new.com',
                    'password1': 'Fr3sh&sh1ny',
                    'password2': 'Fr3sh&sh1ny'}

    def test_valid_form(self):
        form = NewUserForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        data = dict(self.data)
        data['email'] = 'invalid_email'
        form = NewUserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_username(self):
        data = dict(self.data)
        data['username'] = '&^&*##!'
        form = NewUserForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_password(self):
        data = dict(self.data)
        data['password1'] = 'short'
        data['password2'] = 'short'
        form = NewUserForm(data=data)
        self.assertFalse(form.is_valid())


class RecipeAddFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.img = SimpleUploadedFile('example.jpg',
                                     content=open('/home/wroku/Dev/muconfi/mc/media_cdn/tree.JPG', 'rb').read(),
                                     content_type='image/jpeg')

        cls.default_data = {'recipe_name': 'Example Recipe',
                            'preparation_time': 55,
                            'servings': 3,
                            'form-TOTAL_FORMS': 2,
                            'form-INITIAL_FORMS': 0,
                            'form-MIN_NUM_FORMS': 0,
                            'form-MAX_NUM_FORMS': 1000,
                            'form-0-ingredient': 'Somee foood',
                            'form-0-quantity': 100,
                            'directions': 'Somee foood'}

    def setUp(self):
        img = SimpleUploadedFile('example.jpg',
                                 content=open('/home/wroku/Dev/muconfi/mc/media_cdn/tree.JPG', 'rb').read(),
                                 content_type='image/jpeg')
        self.files = {'recipe_image': img}

    def test_valid_recipe_form(self):
        form = RecipeForm(data=self.default_data, files=self.files, collect_ing=[])
        self.assertTrue(form.is_valid())

    def test_invalid_duplicate_name(self):
        """
        Create recipe which will be occupying chosen name to trigger clean_recipe_name
        """

        User.objects.create_superuser('Necessary Evil', 'test@example.com', 'SomeP5WD-40')
        Recipe(recipe_name=self.default_data['recipe_name'], accepted=True, preparation_time=50,
               recipe_image='tree.JPG', directions='blablablab').save()
        form = RecipeForm(data=self.default_data, files=self.files, collect_ing=[])
        self.assertFalse(form.is_valid())
        self.assertIn('This title has already been used. Please type another one.', dict(form.errors)['recipe_name'])


class RecipeIngredientFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = FoodCategory(name='Example Cat')
        cls.category.save()
        cls.ingredient = Ingredient(name='Example Ing',
                                    category=cls.category,
                                    image='tree.JPG',
                                    price=100,
                                    calval=100,
                                    total_carbs=1,
                                    total_fat=1,
                                    total_proteins=1)
        cls.ingredient.save()

    def test_valid_recipe_ingredient(self):
        form = RecipeIngredient({'ingredient': self.ingredient, 'quantity': 20})
        self.assertTrue(form.is_valid())

    def test_invalid_quantity(self):
        form = RecipeIngredient({'ingredient': self.ingredient, 'quantity': 0})
        self.assertFalse(form.is_valid())

        form = RecipeIngredient({'ingredient': self.ingredient, 'quantity': -6})
        self.assertFalse(form.is_valid())

