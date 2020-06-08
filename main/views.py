from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Ingredient
from .forms import ContactForm, RecipeForm, NewUserForm, recipeIngFormset
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import View
# Create your views here.

collect_ing = []


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


def homepage(request):
    greeting = 'We will mix here in a while'
    return render(request, 'main/homepage.html', {'greeting': greeting})


def products(request):
    if request.method == 'POST':
        current_ing = request.POST.get('ingredient')
        if request.POST.get('add') == 'added':
            if current_ing not in collect_ing:
                collect_ing.append(current_ing)
                messages.success(request, f'{current_ing} added to your recipe.')
            else:
                messages.info(request, f'{current_ing} are already on ingredient list.')
        elif request.POST.get('delete') == 'deleted':
            collect_ing.remove(current_ing)
            messages.info(request, f'{current_ing} removed form your recipe. ')
    return render(request, 'main/products.html', {'products': Ingredient.objects.all, 'added': collect_ing})


def detailed_product_page(request, slug):
    obj = get_object_or_404(Ingredient, ingredient_slug=slug)
    template_name = 'main/product_details.html'
    context = {'product': obj}
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
    form = RecipeForm(request.POST or None)
    formset = recipeIngFormset(request.POST or None, initial=[{'ingredient': x} for x in collect_ing])
    if form.is_valid():
        print(form.cleaned_data)
        form = RecipeForm()

    context = {
        'title': 'Lets get to it',
        'form': form,
        'formset': formset,
        'added': collect_ing
    }
    return render(request, 'main/addrecipe.html', context)


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



