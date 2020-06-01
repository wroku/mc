from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Textarea
from .models import Recipe, Quantity, Ingredient


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


'''class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['user', 'recipe_name', 'required_spices', 'directions'],
        widgets = {'directions': Textarea(attrs={'cols': 80, 'rows': 20})},
        #TODO separate directions and add custom validator'''