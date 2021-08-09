from django.contrib import admin

from .models import Favorite, Follow, Ingredient, Recipe, ShoppingList, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ('author', 'name', 'tags')
    list_display = ('name', 'followers')

    @admin.display(empty_value=None)
    def followers(self, obj):
        return obj.favorite_recipe.all().count()


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name', )


admin.site.register(Follow)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
