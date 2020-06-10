from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Textarea
from .models import Recipe, Ingredient
from tinymce.widgets import TinyMCE
from django.forms import formset_factory


class ContactForm(forms.Form):
    full_name = forms.CharField(label='Your name', max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Your email', max_length=100,
                             widget=forms.EmailInput(attrs={'class': 'form-control',  "placeholder": "name@example.com"}))
    content = forms.CharField(label='Your message', max_length=100,
                              widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}))
    level_of_importance = forms.IntegerField(label='Let us know how urgent is the case:', max_value=100,
                                             widget=forms.NumberInput(attrs={'type': 'range', 'class': 'form-control-range'}))


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class RecipeForm(forms.Form):
    recipe_name = forms.CharField(label='Recipe title', max_length=100,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    directions = forms.CharField(label='Provide detailed directions', max_length=10000,
                                 widget=TinyMCE())

    def clean_recipe_name(self, *args, **kwargs):
        recipe_name = self.cleaned_data.get('recipe_name')
        qs = Recipe.objects.filter(recipe_name=recipe_name)
        if qs.exists():
            raise forms.ValidationError('This title has already been used. Please type another one.')
        return recipe_name


class RecipeIngredient(forms.Form):
    ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all())
    quantity = forms.FloatField(label='How much of these?')


RecipeIngFormset = formset_factory(RecipeIngredient, extra=2)



'''class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['user', 'recipe_name', 'required_spices', 'directions'],
        widgets = {'directions': Textarea(attrs={'cols': 80, 'rows': 20})},
        #TODO separate directions and add custom validator'''