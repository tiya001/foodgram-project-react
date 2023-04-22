from django.contrib import admin
from .models import (Ingredient, Tag, Recipe,
                     IngredientInRecipe, ShoppingCart, FavoriteRecipes)
from import_export.admin import ImportExportModelAdmin


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    model = Ingredient
    list_display = ['name', 'measurement_unit']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'text', 'cooking_time']


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'recipe', "amount"]


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
