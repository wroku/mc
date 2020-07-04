"""muconfi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('add-recipe/', views.recipe_page, name='addrecipe'),
    path('contact-us/', views.contact_page, name='contact-page'),
    path('products/', views.products, name='products'),
    path('recipes/', views.recipes, name='recipes'),
    path('products/<str:slug>/', views.detailed_product_page, name='product-details'),
    path('recipes/<str:slug>/', views.detailed_recipe_page, name='recipe-details'),
    path('recipes/<str:slug>/edit', views.edit_recipe, name='recipe-details'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('register/', views.register, name='register'),
    path('account/', views.account_details, name='account'),
    path('search/', views.search, name='search'),
    path('api/data/', views.get_data, name='api-data'),
    path('updateSS/', views.update_session, name='updateSS'),
    path('chartpage/', views.ChartView.as_view(), name='chart-page'),
]


