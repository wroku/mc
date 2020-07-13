from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
from .models import Ingredient, Recipe, Quantity
from .forms import ContactForm, RecipeForm, NewUserForm, RecipeIngFormset, CommentForm, RecipeIngredient, BaseRecipeIngFormSet
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import View
from django.forms import formset_factory
from django.core.mail import send_mail, EmailMessage
import os
from django.template import RequestContext
from itertools import chain
from django.views.generic import ListView

# Create your views here.


def homepage(request):
    greeting = 'We will mix here in a while'
    return render(request, 'main/homepage.html', {'greeting': greeting})


def search(request):
    count = 0
    query = request.GET.get('q', None)
    recipes_qs = Recipe.objects.none()  # just an empty queryset as default
    if query is not None:
        qs = Recipe.objects.search(query)
        qs = sorted(qs,
                    key=lambda instance: instance.recipe_posted,
                    reverse=True)
        count = len(qs)  # since qs is actually a list
        recipes_qs = qs

    template_name = 'main/recipes.html'
    context = {'count': count or 0,
               'query': query,
               'recipes': recipes_qs}

    return render(request, template_name, context)


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

    obj = get_object_or_404(Ingredient, slug=slug)
    current_ing = obj.name
    recipes_containing = Recipe.objects.search_by_ing(obj)

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
               'added': request.session['collect_ing'],
               'recipes_containing': recipes_containing}
    return render(request, template_name, context)


def recipes(request):
    filter_by = request.GET.get('filter', 'recipe_posted')
    ord = request.GET.get('ord', 'desc')
    # ugly solution in 3, 2, 1...
    if ord == 'desc':
        qs = Recipe.objects.order_by('-' + filter_by)
        desc = 'checked'
        asc = ''
    else:
        qs = Recipe.objects.order_by(filter_by)
        desc = ''
        asc = 'checked'
    return render(request,
                  'main/recipes.html',
                  {'desc': desc,
                   'asc': asc,
                   'ordered_by': filter_by,
                   'recipes': qs})


def access_denied(request):
    return render(request,
                  'main/access_denied.html',
                  )


def detailed_recipe_page(request, slug):
    obj = get_object_or_404(Recipe, recipe_slug=slug)

    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.recipe = obj
            new_comment.user = request.user
            new_comment.save()
    else:
        comment_form = CommentForm()

    mnt_profile = [sum([qt.ingredient.total_carbs*qt.quantity for qt in obj.quantities.all()]),
                   sum([qt.ingredient.total_fat*qt.quantity for qt in obj.quantities.all()]),
                   sum([qt.ingredient.total_proteins*qt.quantity for qt in obj.quantities.all()])]
    print(mnt_profile)

    template_name = 'main/recipe_details.html'
    context = {'recipe': obj,
               'quantities': obj.quantities.all(),
               'comments': obj.comments.filter(active=True),
               'new_comment': new_comment,
               'comment_form': comment_form,
               'nutrients': mnt_profile}

    return render(request, template_name, context)


def account_details(request):
    if request.user.is_authenticated:
        return render(request, 'main/account_details.html')
    else:
        return redirect('main:login')


def contact_page(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
        email = EmailMessage(
            'Message from {}, user {}, importance {}/100'.format(form.cleaned_data['full_name'],
                                                                 request.user,
                                                                 form.cleaned_data['level_of_importance'] ),
            form.cleaned_data['content'],
            form.cleaned_data['email'],
            ['wrokuj@gmail.com'],
            reply_to=[form.cleaned_data['email']]
        )
        email.send()
        form = ContactForm()
    context = {
        'title': 'Contact us',
        'form': form,
    }
    return render(request, 'main/contact_form.html', context)


def recipe_page(request):
    # TODO Change fs to BaseRecipeIngFormset with distinct ingredient validation and test the fuck out of it
    if 'collect_ing' not in request.session:
        request.session['collect_ing'] = []
    form = RecipeForm(request.POST or None, request.FILES or None,
                      collect_ing=request.session['collect_ing'])
    formset = RecipeIngFormset(request.POST or None,
                               form_kwargs={'collect_ing': request.session['collect_ing']},
                               initial=[{'ingredient': x} for x in request.session['collect_ing']])
    if request.method == 'POST':
        print('Here we GO:')
        print(request.session['collect_ing'])
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
            return redirect(f'/recipes/{recipe.recipe_slug}')
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
    instance = get_object_or_404(Recipe, recipe_slug=slug)
    if request.user != instance.user:
        return redirect('/access_denied')
    request.session['collect_ing'] = []
    form = RecipeForm(request.POST or None, request.FILES or None,
                      editing=instance.recipe_name,
                      initial={'recipe_name': instance.recipe_name,
                               'recipe_image': instance.recipe_image,
                               'preparation_time': instance.preparation_time,
                               'directions': instance.directions})

    # qs = Quantity.objects.filter(recipe=instance.recipe_name)
    qs = instance.quantities.all()
    formset_initial_data = [{'ingredient': obj.ingredient, 'quantity': obj.quantity} for obj in qs]
    for obj in qs[:len(qs)-1]:
        request.session['collect_ing'].append(str(obj.ingredient))
    # Somewhat hacky but I couldn't find how to pass extra kwarg to formset factory + and-or trick from diving in python
    RecipeEditIngFormset = formset_factory(RecipeIngredient,
                                           formset=BaseRecipeIngFormSet,
                                           extra=(formset_initial_data and [0] or [1])[0])
    formset = RecipeEditIngFormset(request.POST or None,
                                   form_kwargs={'collect_ing': request.session['collect_ing']},
                                   initial=formset_initial_data)
    if request.method == 'POST':
        print('Here we GO:')
        print(request.session['collect_ing'])
        if form.is_valid() and formset.is_valid():
            for key, value in form.cleaned_data.items():
                setattr(instance, key, value)

            # maybe clean {}s from cleaned data if you cant write custom formset validation?
            index = 0
            for fieldset, qt in zip(formset.cleaned_data, qs):
                for key, value in fieldset.items():
                    setattr(qt, key, value)
                qt.save()
                index += 1
            if len(formset.cleaned_data) > len(qs):
                for fieldset in formset.cleaned_data[index:]:
                    if fieldset != {}:
                        nq = Quantity.objects.create(recipe=instance,
                                                     ingredient=fieldset['ingredient'],
                                                     quantity=fieldset['quantity'])

            elif len(qs) > len(formset.cleaned_data):
                for qt in qs[index:]:
                    qt.delete()

            instance.save()
            request.session['collect_ing'] = []
            request.session.modified = True
            form = RecipeForm(collect_ing=request.session['collect_ing'])
            formset = RecipeIngFormset(form_kwargs={'collect_ing': request.session['collect_ing']})
            return redirect(f'/recipes/{instance.recipe_slug}')

        else:
            messages.error(request, f"Invalid data!")
            print(formset.errors)

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
                redirect_to = request.POST.get('next', '/')
                return HttpResponseRedirect(redirect_to)
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
    form = AuthenticationForm()
    return render(request,
                  'main/login.html',
                  context={'form': form})


def logout_request(request):

    redirect_to = request.GET.get('next', '/')
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'Logged out succesfully!')
        return HttpResponseRedirect(redirect_to)
    else:
        messages.info(request, 'You are not logged in.')
        return HttpResponseRedirect(redirect_to)


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


