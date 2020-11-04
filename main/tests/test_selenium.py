from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from django.contrib.auth.models import User
from main.models import Ingredient, FoodCategory, Recipe, Quantity
from django.core.files.uploadedfile import SimpleUploadedFile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class RecipeRelatedTest(StaticLiveServerTestCase):
    """
    Base class for functional tests dealing with recipes. Simple setup defined to avoid repetition.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.username = 'test_user'
        self.password = 'herewego'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)

        self.category = FoodCategory(name='Example Cat')
        self.category.save()
        img = SimpleUploadedFile('example.jpg',
                                 content=open('/home/wroku/Dev/muconfi/mc/media_cdn/tree.JPG', 'rb').read(),
                                 content_type='image/jpeg')
        defaults = {'name': 'Ing',
                    'category': self.category,
                    'image': img,
                    'price': 10,
                    'calval': 100,
                    'total_carbs': 10,
                    'total_fat': 10,
                    'total_proteins': 10,
                    'accepted': True}

        self.NUMBER_OF_INGREDIENTS = 5
        for i in range(1, self.NUMBER_OF_INGREDIENTS + 1):
            defaults['name'] = defaults['name'][:3] + str(i)
            ingredient = Ingredient(**defaults)
            ingredient.save()

        self.recipe = Recipe(recipe_name='Model recipe', accepted=True, preparation_time=50,
                             recipe_image='tree.JPG', directions='Ing')
        self.recipe.save()
        for i in range(1, self.NUMBER_OF_INGREDIENTS + 1):
            Quantity(recipe=self.recipe,
                     ingredient=Ingredient.objects.get(name=f'Ing{i}'),
                     quantity=100 + i).save()


class UserTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.username = 'test_user'
        self.password = 'herewego'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(self.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(self.password)
        self.selenium.find_element_by_xpath('//button[text()="Login"]').click()
        self.selenium.implicitly_wait(10)
        self.assertEqual(self.selenium.current_url, f'{self.live_server_url}/')

    def test_login_redirect(self):
        """
        Check if login page accessed from entry_point successfully redirect back after authorization.
        """

        entry_point = '/recipes/'
        self.selenium.get('%s%s' % (self.live_server_url, entry_point))
        self.selenium.find_element_by_xpath('//a[text()="Login"]').click()
        self.selenium.find_element_by_name("username").send_keys(self.username)
        self.selenium.find_element_by_name("password").send_keys(self.password)
        self.selenium.find_element_by_xpath('//button[text()="Login"]').click()
        self.assertEqual(self.selenium.current_url, f'{self.live_server_url}{entry_point}')

    def test_logout_redirect(self):
        """
        Check if logout page accessed directly while user is not logged in redirects to frontpage.
        """

        self.selenium.get(f'{self.live_server_url}/logout')
        self.assertEqual(self.selenium.current_url, f'{self.live_server_url}/')


class RecipeAddTest(RecipeRelatedTest):

    def test_add_valid_recipe(self):
        recipe_title = 'Example Recipe'
        self.selenium.get(f'{self.live_server_url}/add-recipe')
        self.selenium.find_element_by_id('id_recipe_name').send_keys('Example recipe')
        self.selenium.find_element_by_name('recipe_image').send_keys('/home/wroku/Dev/muconfi/mc/media_cdn/tree.JPG')
        self.selenium.find_element_by_id('id_preparation_time').send_keys(44)
        servings = Select(self.selenium.find_element_by_id('id_servings'))
        servings.select_by_index(3)
        self.selenium.execute_script("window.scrollTo(0, 1000);")

        for i in range(self.NUMBER_OF_INGREDIENTS):
            ingredient = Select(self.selenium.find_element_by_id(f'id_form-{i}-ingredient'))
            ingredient.select_by_index(1)
            self.selenium.find_element_by_id(f'id_form-{i}-quantity').send_keys(100)
            self.selenium.find_element_by_xpath('//button[text()="+"]').click()

        self.selenium.find_element_by_id('id_directions_ifr').send_keys('Ing Ing')
        self.selenium.find_element_by_xpath('//button[text()="Create"]').click()
        self.assertEqual(self.selenium.current_url,
                         f'{self.live_server_url}/recipes/{"-".join(recipe_title.lower().split())}/')

    def test_excluding_from_options(self):
        """
        After entering ingredient in formset row next row should not contain this particular option in select menu.
        """

        self.selenium.get(f'{self.live_server_url}/add-recipe')
        ingredient = Select(self.selenium.find_element_by_id(f'id_form-0-ingredient'))
        chosen_ing = ingredient.options[1].text
        ingredient.select_by_index(1)
        self.selenium.find_element_by_id(f'id_form-0-quantity').send_keys(100)
        self.selenium.find_element_by_xpath('//button[text()="+"]').click()

        ingredient2 = Select(self.selenium.find_element_by_id(f'id_form-1-ingredient'))
        select2_options = [option.text for option in ingredient2.options]
        self.assertNotIn(chosen_ing, select2_options)


class RecipeDetailsPageTest(RecipeRelatedTest):

    def test_servings_js_add(self):
        """
        Testing feature allowing to add servings, checking if quantities of ingredients in recipe details page
        increase accordingly.
        """

        self.selenium.get(f'{self.live_server_url}/recipes/{self.recipe.recipe_slug}')
        number_of_servings = self.selenium.find_element_by_id('numberOfServings')
        qt1_initial = self.selenium.find_element_by_xpath('(//span[@class="quantity"])[1]').text
        qt2_initial = self.selenium.find_element_by_xpath('(//span[@class="quantity"])[2]').text

        self.assertEqual(int(number_of_servings.text), self.recipe.servings)
        self.selenium.find_element_by_xpath('//button[text()="+"]').click()
        self.assertEqual(int(number_of_servings.text), self.recipe.servings + 1)

        qt1 = self.selenium.find_element_by_xpath('(//span[@class="quantity"])[1]').text
        qt2 = self.selenium.find_element_by_xpath('(//span[@class="quantity"])[2]').text

        self.assertEqual(float(qt1_initial)/(int(number_of_servings.text)-1),
                         float(qt1)/int(number_of_servings.text))
        self.assertEqual(float(qt2_initial) / (int(number_of_servings.text) - 1),
                         float(qt2) / int(number_of_servings.text))

    def test_servings_js_subtract(self):
        """
        Testing feature allowing to subtract servings, checking if quantities of ingredients in recipe details page
        decrease accordingly.
        """

        self.selenium.get(f'{self.live_server_url}/recipes/{self.recipe.recipe_slug}')
        number_of_servings = self.selenium.find_element_by_id('numberOfServings')
        qt1_initial = self.selenium.find_element_by_xpath('(//span[@class="quantity"])[1]').text
        qt2_initial = self.selenium.find_element_by_xpath('(//span[@class="quantity"])[2]').text
        self.assertEqual(int(number_of_servings.text), self.recipe.servings)
        self.selenium.find_element_by_xpath('//button[text()="-"]').click()
        self.assertEqual(int(number_of_servings.text), self.recipe.servings - 1)
        qt1 = self.selenium.find_element_by_xpath('(//span[@class="quantity"])[1]').text
        qt2 = self.selenium.find_element_by_xpath('(//span[@class="quantity"])[2]').text
        self.assertEqual(float(qt1_initial) / (int(number_of_servings.text) + 1),
                         float(qt1) / int(number_of_servings.text))
        self.assertEqual(float(qt2_initial) / (int(number_of_servings.text) + 1),
                         float(qt2) / int(number_of_servings.text))

    def test_servings_js_constraint(self):
        """
        Make sure that number of servings cannot be decreased below 1.
        """

        self.selenium.get(f'{self.live_server_url}/recipes/{self.recipe.recipe_slug}')
        number_of_servings = self.selenium.find_element_by_id('numberOfServings')
        self.assertEqual(int(number_of_servings.text), self.recipe.servings)
        decrease_btn = self.selenium.find_element_by_xpath('//button[text()="-"]')
        for _ in range(self.recipe.servings + 3):
            decrease_btn.click()
        self.assertEqual(int(number_of_servings.text), 1)

    def test_anonymous_comment(self):
        self.selenium.get(f'{self.live_server_url}/recipes/{self.recipe.recipe_slug}')
        comment_section = self.selenium.find_element_by_xpath('//div[@class="comments-section-standard"]/div')
        self.assertEqual(comment_section.text,
                         "Comments are available for logged users only. Sign in to share your opinion or "
                         "register if you don't have an account yet.")

    def test_logged_in_user_comment(self):
        self.selenium.get(f'{self.live_server_url}/recipes/{self.recipe.recipe_slug}')
        self.selenium.find_element_by_xpath('//a[text()="Login"]').click()
        self.selenium.find_element_by_name("username").send_keys(self.username)
        self.selenium.find_element_by_name("password").send_keys(self.password)
        self.selenium.find_element_by_xpath('//button[text()="Login"]').click()
        comment_section = self.selenium.find_element_by_xpath('//div[@class="comments-section-standard"]')
        self.assertEqual(comment_section.text,
                         'Leave a comment\nShare your opinions, experience, advices or let '
                         'others know about tasty variations of this recipe!\nSubmit')

    def test_add_comment(self):
        self.selenium.get(f'{self.live_server_url}/recipes/{self.recipe.recipe_slug}')
        self.selenium.find_element_by_xpath('//a[text()="Login"]').click()
        self.selenium.find_element_by_name("username").send_keys(self.username)
        self.selenium.find_element_by_name("password").send_keys(self.password)
        self.selenium.find_element_by_xpath('//button[text()="Login"]').click()
        comment_input = self.selenium.find_elements_by_xpath('//textarea')[1]
        comment_input.click()
        actions = ActionChains(self.selenium)
        actions.send_keys('Example content')
        actions.perform()
        self.selenium.find_elements_by_xpath('//button[text()="Submit"]')[1].click()
        comment_section = self.selenium.find_element_by_xpath('//div[@class="comments-section-standard"]/div')
        self.assertEqual(comment_section.text, 'Your comment is awaiting moderation.')


class RecipeEditTest(RecipeRelatedTest):

    def test_prepopulated_fields(self):
        """
        Check correctness of prepopulated fields on edit page.
        """

        self.selenium.get(f'{self.live_server_url}/recipes/{self.recipe.recipe_slug}/edit')
        title = self.selenium.find_element_by_id('id_recipe_name').get_attribute('value')
        preparation_time = self.selenium.find_element_by_id('id_preparation_time').get_attribute('value')
        servings = Select(self.selenium.find_element_by_id('id_servings'))
        self.assertEqual(title, self.recipe.recipe_name)
        self.assertEqual(int(preparation_time), self.recipe.preparation_time)
        self.assertEqual(int(servings.first_selected_option.text), self.recipe.servings)

        number_of_initial_ings = int(self.selenium.find_element_by_id('id_form-INITIAL_FORMS').get_attribute('value'))
        qts = self.recipe.quantities.all()
        for i in range(number_of_initial_ings):
            ingredient = Select(self.selenium.find_element_by_id(f'id_form-{i}-ingredient')).first_selected_option.text
            qt = float(self.selenium.find_element_by_id(f'id_form-{i}-quantity').get_attribute('value'))
            self.assertEqual(ingredient, qts[i].ingredient.name)
            self.assertEqual(qt, qts[i].quantity)

        self.selenium.switch_to.frame(self.selenium.find_element_by_id('id_directions_ifr'))
        editor_initial_content = self.selenium.find_element_by_id('tinymce').text
        self.assertEqual(editor_initial_content, self.recipe.directions)

    def test_simple_edit_recipe(self):
        """
        Enter new preparation time and save instance, checking if changes are reflected in database.
        """

        new_pt_value = 33
        self.selenium.get(f'{self.live_server_url}/recipes/{self.recipe.recipe_slug}/edit')
        self.selenium.find_element_by_id('id_preparation_time').clear()
        self.selenium.find_element_by_id('id_preparation_time').send_keys(new_pt_value)
        self.selenium.find_element_by_xpath('//button[text()="Save"]').click()

        self.assertEqual(new_pt_value, Recipe.objects.get(recipe_name=self.recipe.recipe_name).preparation_time)


class SearchByIngredientsTest(RecipeRelatedTest):

    def test_recipe_containing_search(self):
        """
        Add all possible ingredients to list and use button to initialize search. Check if final url is correct and
        ends with properly formulated query. Search should return 'Model recipe' instance.
        """

        self.selenium.get(f'{self.live_server_url}/products')
        for i in range(self.NUMBER_OF_INGREDIENTS):
            add_btn = self.selenium.find_element_by_xpath('//button[@name="add"]')
            add_btn.click()
        self.selenium.find_element_by_xpath('//span[text()="Search for recipe"]').click()
        ings = [ing.name for ing in Ingredient.objects.all()]
        self.assertEqual(self.selenium.current_url, f'{self.live_server_url}/search-by-ingredients/{"&".join(ings)}/')
        result_title = self.selenium.find_element_by_xpath('//h3[@class="card-title"]').text
        self.assertEqual(result_title, self.recipe.recipe_name)

    def test_buy_list(self):
        number_of_excluded = 2
        self.selenium.get(f'{self.live_server_url}/products')
        for i in range(self.NUMBER_OF_INGREDIENTS - number_of_excluded):
            add_btn = self.selenium.find_element_by_xpath('//button[@name="add"]')
            add_btn.click()
        self.selenium.find_element_by_xpath('//span[text()="Search for recipe"]').click()

        not_included = [ing.name for ing in Ingredient.objects.all()][-number_of_excluded:]
        to_buy_list = [ing.text for ing in self.selenium.find_elements_by_class_name('alert-secondary')]
        self.assertEqual(not_included, to_buy_list)






