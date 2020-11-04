from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
from .models import Ingredient, Recipe, Quantity, Comment
from .forms import ContactForm, RecipeForm, NewUserForm, RecipeIngFormset, CommentForm, RecipeIngredient, BaseRecipeIngFormSet
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import View
from django.forms import formset_factory
from django.core.mail import EmailMessage
from django.views.generic.edit import CreateView
from django.core.exceptions import ObjectDoesNotExist
import os
# Create your views here.


def homepage(request):
    return render(request, 'main/homepage.html')


class IngredientCreate(CreateView):
    model = Ingredient
    fields = ['name', 'category', 'price', 'calval', 'image',
              'total_carbs', 'total_fat', 'total_proteins']


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
    else:
        # count = -1 triggers displaying info how to use search feature
        qs = recipes_qs
        count = -1

    filter_by = request.GET.get('filter', 'recipe_posted')
    ord = request.GET.get('ord', 'desc')

    # ugly solution in 3, 2, 1...
    if ord == 'desc':
        recipes_qs = sorted(qs,
                            key=lambda instance: getattr(instance, filter_by),
                            reverse=True)
        desc = 'checked'
        asc = ''
    else:
        recipes_qs = sorted(qs,
                            key=lambda instance: getattr(instance, filter_by),)
        desc = ''
        asc = 'checked'

    # Hacking around nice-looking card columns screwing up my ordering.
    # Works just fine with similar heights of recipe images.
    recipes_qs = recipes_qs[::2] + recipes_qs[1::2]

    template_name = 'main/recipes.html'

    # asc, desc and ordered_by variables used by js in template to preserve data beetween reloads
    context = {'desc': desc,
               'asc': asc,
               'ordered_by': filter_by,
               'count': count,
               'query': query,
               'recipes': recipes_qs}

    return render(request, template_name, context)


def recipes_containing(request, query=None):
    results = []

    def search(subquery, excluded=None):
        """
        Return tuple with matches and additional data, ready to be displayed in a template.

        -> (((recipe, [missing]),(...)), subquery, number of results)
        [missing] - ingredients listed in particular recipe but not included in user's query
        When excluded is provided, use queryset difference to subtract recipes possibly duplicated
        in full and partial length query.
        """
        partial_matches = []
        for ing in subquery:
            partial_matches.append(Recipe.objects.search_by_ing(ing))
        if partial_matches:
            recipes_qs = partial_matches[0].intersection(*partial_matches[1:])
            if excluded:
                recipes_qs = recipes_qs.difference(Recipe.objects.search_by_ing(excluded))
        else:
            recipes_qs = Recipe.objects.none()

        missING = []
        for recipe in recipes_qs:
            missing = []
            for quantity in recipe.quantities.all():
                if quantity.ingredient not in subquery:
                    missing.append(quantity.ingredient)
            missING.append(missing)
        return (tuple(zip(recipes_qs, missING)), subquery, len(recipes_qs))

    if query:
        query = [Ingredient.objects.get(name=name) for name in query.split('&')]

        results.append(search(query))

        # If there is no more than five exact matches, perform additional searches,
        # each excluding one of the ingredients.
        if results[0][2] < 5 and len(query) >= 2:
            for i in range(1, len(query)+1):
                results.append(search(query[:len(query) - i] + query[len(query) + 1 - i:], query[-i]))

    template_name = 'main/recipes_containing.html'
    context = {'ingredients': Ingredient.objects.all(),
               'recipes': results,
               }

    return render(request, template_name, context)


def products(request):
    if 'collect_ing' not in request.session or request.session['collect_ing'] == '':
        request.session['collect_ing'] = []

    count = 0
    query = request.GET.get('q', None)
    ingredients_qs = Ingredient.objects.none()
    if query is not None:
        ingredients_qs = Ingredient.objects.search(query)
        count = len(ingredients_qs)
    if request.method == 'POST':
        try:
            Ingredient.objects.get(name=request.POST.get('ingredient'))
            current_ing = request.POST.get('ingredient')
            if request.POST.get('add') == 'added':
                if current_ing not in request.session['collect_ing']:
                    request.session['collect_ing'].append(current_ing)
                    request.session.modified = True
                else:
                    messages.info(request, f'{current_ing} is already on ingredient list.')
            elif request.POST.get('delete') == 'deleted':
                if current_ing in request.session['collect_ing']:
                    request.session['collect_ing'].remove(current_ing)
                    request.session.modified = True
                else:
                    messages.info(request, f'{current_ing} is not on ingredient list.')
        except ObjectDoesNotExist:
            messages.info(request, 'Such ingredient does not even exist. Stop messing with my site.')
        if request.POST.get('clear') == 'cleared':
            request.session['collect_ing'] = []
            request.session.modified = True
    return render(request, 'main/products.html', {'products': Ingredient.objects.filter(accepted=True),
                                                  'added': request.session['collect_ing'],
                                                  'count': count,
                                                  'ingredients': ingredients_qs,
                                                  'query': query})


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

    qs = qs.filter(accepted=True)
    # Hacking around nice-looking card columns screwing up my ordering.
    # Works just fine with similar heights of recipe images.
    qs = qs[::2] + qs[1::2]

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

    mnt_profile = [(sum([qt.ingredient.total_carbs*qt.quantity for qt in obj.quantities.all()]))/obj.servings,
                   (sum([qt.ingredient.total_fat*qt.quantity for qt in obj.quantities.all()]))/obj.servings,
                   (sum([qt.ingredient.total_proteins*qt.quantity for qt in obj.quantities.all()]))/obj.servings]

    template_name = 'main/recipe_details.html'
    context = {'recipe': obj,
               'quantities': obj.quantities.all(),
               'comments': obj.comments.filter(active=True),
               'new_comment': new_comment,
               'comment_form': comment_form,
               'nutrients': mnt_profile}

    return render(request, template_name, context)


@login_required()
def account_details(request):
    context = {'recipes': Recipe.objects.filter(user=request.user),
               'comments': Comment.objects.filter(user=request.user)}
    return render(request, 'main/account_details.html', context)


def contact_page(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        email = EmailMessage(
            'Message from {}, user {}, importance {}/100'.format(form.cleaned_data['full_name'],
                                                                 request.user,
                                                                 form.cleaned_data['level_of_importance']),
            form.cleaned_data['content'],
            form.cleaned_data['email'],
            ['wrokuj@gmail.com'],
            reply_to=[form.cleaned_data['email']]
        )
        print(os.environ.get('EMAIL_HOST_PASSWORD'))
        email.send()
        form = ContactForm()
    context = {
        'title': 'Contact us',
        'form': form,
    }
    return render(request, 'main/contact_form.html', context)


def recipe_page(request):
    if 'collect_ing' not in request.session:
        request.session['collect_ing'] = []
    form = RecipeForm(request.POST or None, request.FILES or None,
                      collect_ing=request.session['collect_ing'])
    formset = RecipeIngFormset(request.POST or None,
                               #  form_kwargs={'collect_ing': request.session['collect_ing']},
                               initial=[{'ingredient': x} for x in request.session['collect_ing']])
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            recipe = Recipe.objects.create(**form.cleaned_data)
            if request.user.is_authenticated:
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
    context = {
        'title': 'Recipe',
        'form': form,
        'formset': formset,
        'added': request.session['collect_ing']
    }
    return render(request, 'main/addrecipe.html', context)


def edit_recipe(request, slug):
    instance = get_object_or_404(Recipe, recipe_slug=slug)
    if instance.user and request.user != instance.user:
        return redirect('/access_denied')
    request.session['collect_ing'] = []
    form = RecipeForm(request.POST or None, request.FILES or None,
                      editing=instance.recipe_name,
                      collect_ing=request.session['collect_ing'],
                      initial={'recipe_name': instance.recipe_name,
                               'recipe_image': instance.recipe_image,
                               'preparation_time': instance.preparation_time,
                               'servings': instance.servings,
                               'directions': instance.directions})

    qs = instance.quantities.all()
    formset_initial_data = [{'ingredient': obj.ingredient, 'quantity': obj.quantity} for obj in qs]
    if qs:
        for obj in qs[:len(qs)-1]:
            '''Avoid adding last ing to session in order to retain "+" icon in last row'''
            request.session['collect_ing'].append(str(obj.ingredient))
    RecipeEditIngFormset = formset_factory(RecipeIngredient,
                                           formset=BaseRecipeIngFormSet,
                                           extra=(formset_initial_data and [0] or [1])[0])
    formset = RecipeEditIngFormset(request.POST or None,
                                   # form_kwargs={'collect_ing': request.session['collect_ing']},
                                   initial=formset_initial_data)
    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():
            for key, value in form.cleaned_data.items():
                setattr(instance, key, value)

            index = 0
            for fieldset, qt in zip(formset.cleaned_data, qs):
                for key, value in fieldset.items():
                    setattr(qt, key, value)
                qt.save()
                index += 1
            if len(formset.cleaned_data) > len(qs):
                for fieldset in formset.cleaned_data[index:]:
                    if fieldset != {}:
                        Quantity.objects.create(recipe=instance,
                                                ingredient=fieldset['ingredient'],
                                                quantity=fieldset['quantity'])

            elif len(qs) > len(formset.cleaned_data):
                for qt in qs[index:]:
                    qt.delete()

            instance.save()
            request.session['collect_ing'] = []
            request.session.modified = True
            return redirect(f'/recipes/{instance.recipe_slug}')

        else:
            messages.error(request, f"Invalid data!")

    context = {'recipe': instance,
               'title': 'Edit Recipe',
               'form': form,
               'formset': formset,
               'added': request.session['collect_ing']}

    return render(request, 'main/addrecipe.html', context)


def update_session(request):
    if not request.is_ajax() or not request.method == 'POST':
        return HttpResponseNotAllowed(['POST'])
    # TODO Maybe if editing in request.session...
    if request.method == 'POST':
        updateING = request.POST.get('ingredients', [])
        if updateING:
            updateING = updateING.strip('#').split('#')
            updateING = list(dict.fromkeys(updateING))
        request.session['collect_ing'] = updateING
        request.session.modified = True
        return HttpResponse('ok')
# id_form-2-ingredient


def update_options(request):
    if not request.is_ajax() or not request.method == 'GET':
        return HttpResponseNotAllowed(['GET'])
    if request.method == 'GET':
        ings = Ingredient.objects.exclude(name__in=request.session['collect_ing'])
    return render(request, 'main/new_row_options.html', {'ingredients': ings})


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




