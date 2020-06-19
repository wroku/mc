from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from .models import Ingredient, Recipe, Quantity
from .forms import ContactForm, RecipeForm, NewUserForm, RecipeIngFormset
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import View
from django.template import RequestContext

# Create your views here.


def homepage(request):
    greeting = 'We will mix here in a while'
    return render(request, 'main/homepage.html', {'greeting': greeting})


def products(request):
    if 'collect_ing' not in request.session or request.session['collect_ing'] == '':
        request.session['collect_ing'] = []
    if request.method == 'POST':
        current_ing = request.POST.get('ingredient')
        if request.POST.get('add') == 'added':
            if current_ing not in request.session['collect_ing']:
                request.session['collect_ing'].append(current_ing)
                request.session.modified = True
                messages.success(request, f'{current_ing} added to your recipe.')
            else:
                messages.info(request, f'{current_ing} are already on ingredient list.')
        elif request.POST.get('delete') == 'deleted':
            if current_ing in request.session['collect_ing']:
                request.session['collect_ing'].remove(current_ing)
                request.session.modified = True
                messages.info(request, f'{current_ing} removed form your recipe. ')
            else:
                messages.info(request, f'{current_ing} is not on ingredient list.')
    return render(request, 'main/products.html', {'products': Ingredient.objects.all, 'added': request.session['collect_ing']})


def detailed_product_page(request, slug):
    if 'collect_ing' not in request.session or request.session['collect_ing'] == '':
        request.session['collect_ing'] = []

    obj = get_object_or_404(Ingredient, ingredient_slug=slug)
    current_ing = obj.ingredient_name

    if request.method == 'POST':
        if request.POST.get('add') == 'added':
            if current_ing not in request.session['collect_ing']:
                request.session['collect_ing'].append(current_ing)
                request.session.modified = True
                messages.success(request, f'{current_ing} added to your recipe.')
            else:
                messages.info(request, f'{current_ing} are already on ingredient list.')
        elif request.POST.get('delete') == 'deleted':
            if current_ing in request.session['collect_ing']:
                request.session['collect_ing'].remove(current_ing)
                request.session.modified = True
                messages.info(request, f'{current_ing} removed form your recipe. ')
            else:
                messages.info(request, f'{current_ing} is not on ingredient list.')

    template_name = 'main/product_details.html'
    context = {'product': obj,
               'added': request.session['collect_ing']}
    return render(request, template_name, context)


def detailed_recipe_page(request, slug):
    obj = get_object_or_404(Recipe, recipe_slug=slug)
    template_name = 'main/recipe_details.html'
    context = {'recipe': obj,
               'quantities': obj.quantities.all()}
    return render(request, template_name, context)


def account_details(request):
    if request.user.is_authenticated:
        return render(request, 'main/account_details.html' )
    else:
        return redirect('main:login')


def contact_page(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
        form = ContactForm()
    context = {
        'title': 'Contact us',
        'form': form
    }
    return render(request, 'main/contact_form.html', context)


def recipe_page(request):
    if 'collect_ing' not in request.session:
        request.session['collect_ing'] = []
    form = RecipeForm(request.POST or None, request.FILES or None,
                      collect_ing=request.session['collect_ing'])
    formset = RecipeIngFormset(request.POST or None,
                               form_kwargs={'collect_ing': request.session['collect_ing']},
                               initial=[{'ingredient': x} for x in request.session['collect_ing']])
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            recipe = Recipe.objects.create(**form.cleaned_data)
            recipe.user = request.user
            for fieldset in formset.cleaned_data:
                if fieldset != {}:
                    f1 = Quantity.objects.create(recipe=recipe,
                                                 ingredient=fieldset['ingredient'],
                                                 quantity=fieldset['quantity'])
                    f1.save()
            recipe.save()
            request.session['collect_ing'] = []
            request.session.modified = True
            form = RecipeForm(collect_ing=request.session['collect_ing'])
            formset = RecipeIngFormset(form_kwargs={'collect_ing': request.session['collect_ing']})
            messages.info(request, f"Success")
        else:
            messages.error(request, f"Invalid data!")
            print(formset.errors)
    context = {
        'title': 'Recipe',
        'form': form,
        'formset': formset,
        'added': request.session['collect_ing']
    }
    return render(request, 'main/addrecipe.html', context)


def edit_recipe(request, slug):
    if 'collect_ing' not in request.session:
        request.session['collect_ing'] = []
    instance = get_object_or_404(Recipe, recipe_slug=slug)
    form = RecipeForm(request.POST or None, request.FILES or None,
                      initial={'recipe_name': instance.recipe_name,
                               'recipe_image': instance.recipe_image,
                               'preparation_time': instance.preparation_time,
                               'directions': instance.directions})

    # qs = Quantity.objects.filter(recipe=instance.recipe_name)

    qs = instance.quantities.all()
    formset_initial_data = [{'ingredient': obj.ingredient, 'quantity': obj.quantity} for obj in qs]
    formset = RecipeIngFormset(request.POST or None,
                               form_kwargs={'collect_ing': request.session['collect_ing']},
                               initial=formset_initial_data)

    context = {
        'recipe': instance,
        'title': 'Edit Recipe',
        'form': form,
        'formset': formset,
        'added': request.session['collect_ing']
    }
    return render(request, 'main/addrecipe.html', context)


def update_session(request):

    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    # TODO Maybe if editing in request.session...
    if request.method == 'POST':
        updateING = request.POST.get('ingredients', [])
        print(updateING)
        if updateING:
            updateING = updateING.strip('#').split('#')
            updateING = list(dict.fromkeys(updateING))
        request.session['collect_ing'] = updateING
        request.session.modified = True
        return HttpResponse('ok')


def register(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'New account created: {username}')
            login(request, user)
            messages.info(request, f'You are now logged in as {username}')
            return redirect('main:homepage')
        else:
            for msg in form.error_messages:
                messages.error(request, f'{msg}: {form.error_messages[msg]}')
    form = NewUserForm
    return render(request,
                  'main/register.html',
                  context={'form': form})


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged as {username}')
                return redirect('main:homepage')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
    form = AuthenticationForm()
    return render(request,
                  'main/login.html',
                  context={'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, 'Logged out succesfully!')
    return redirect('main:homepage')


class ChartView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'main/chart.html', {})


def get_data(request, *args, **kwargs):
    qs = Ingredient.objects
    labels = ['pushups', 'pullups', 'squats']
    default_items = [150, 66, 48]
    data = {
        'labels': labels,
        'default': default_items,
    }
    return JsonResponse(data)


