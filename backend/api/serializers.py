import re
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import (CustomUser, Favorite, Ingredient,
                     IngredientInRecipe, Recipe, ShoppingList, Tag)
from users.models import Follow


class BaseUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

    def validate_hex_color(self, data):
        color = self.initial_data.get('hex_color')
        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color)
        if not match:
            raise serializers.ValidationError('hex is not valid')
        
        return data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    queryset = CustomUser.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = (
            'user',
            'author'
        )

    def validate(self, data):
        user = self.context.get('request').user
        author_id = data['author'].id
        follow_exist = Follow.objects.filter(
            user=user,
            author__id=author_id
        ).exists()

        if self.context.get('request').method == 'GET':
            if user.id == author_id or follow_exist:
                raise serializers.ValidationError(
                    'Подписка существует')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowFollowersSerializer(
            instance.author,
            context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )

    def validate(self, data):
        user = self.context.get('request').user
        recipe_id = data['recipe'].id

        if (self.context.get('request').method == 'GET'
                and Favorite.objects.filter(user=user,
                                            recipe__id=recipe_id).exists()):
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное')

        recipe = get_object_or_404(Recipe, id=recipe_id)

        if (self.context.get('request').method == 'DELETE'
                and not Favorite.objects.filter(
                    user=user,
                    recipe=recipe).exists()):
            raise serializers.ValidationError()

        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShowRecipeSerializer(
            instance.recipe,
            context=context).data


class ShoppingListSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingList

    def validate(self, data):
        user = self.context.get('request').user
        recipe_id = data['recipe'].id
        if (self.context.get('request').method == 'GET'
                and ShoppingList.objects.filter(
                    user=user,
                    recipe__id=recipe_id
                ).exists()):
            raise serializers.ValidationError(
                'Продукты уже в корзине')

        recipe = get_object_or_404(Recipe, id=recipe_id)

        if (self.context.get('request').method == 'DELETE'
                and not ShoppingList.objects.filter(
                    user=user,
                    recipe=recipe).exists()):
            raise serializers.ValidationError()

        return data

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'purchases')


class AddFavouriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ListRecipeUserSerializer(BaseUserSerializer):
    #is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    #def get_is_subscribed(self, obj):
    #    request = self.context.get('request')
    #    if request is None or request.user.is_anonymous:
    #        return False
    #    return Follow.objects.filter(user=request.user, author=obj).exists()


class FlagSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingList.objects.filter(recipe=obj, user=user).exists()


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientInRecipe
        fields = '__all__'


class IngredientInRecipeSerializerToCreateRecipe(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    #name = serializers.ReadOnlyField(source='ingredient.name')
    name = serializers.SlugRelatedField(
        source='ingredient.name',
        read_only=True,
        slug_field='name'
    )
    #measurement_unit = serializers.ReadOnlyField(
    #    source='ingredient.measurement_unit'
    #)
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient.measurement_unit',
        read_only=True,
        slug_field='measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ListRecipeSerializer(FlagSerializer):
    author = ListRecipeUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta(FlagSerializer.Meta):
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        #qs = IngredientInRecipe.objects.filter(recipe=obj)
        #qs = IngredientInRecipe.objects.get(related_name=obj)
        qs = IngredientInRecipe.objects.select_related('recipes_ingredients_list')
        return IngredientInRecipeSerializerToCreateRecipe(qs, many=True).data


class RecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        max_length=None,
        required=True,
        allow_empty_file=False,
        use_url=True,
    )
    author = ListRecipeUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'



class ShowFollowerRecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        max_length=None,
        required=True,
        allow_empty_file=False,
        use_url=True,
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowFollowersSerializer(BaseUserSerializer):
    recipes = ShowFollowerRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField('count_author_recipes')

    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def count_author_recipes(self, user):
        #return len(user.recipes.all())
        return user.recipes.count()

    #def check_if_subscribed(self, user):
    #    current_user = self.context.get('current_user')
    #    other_user = user.following.all()
    #    if user.is_anonymous:
    #        return False
        #if other_user.count() == 0:
        #    return False
    #    if Follow.objects.filter(user=user, author=current_user).exists():
    #        return True
    #    return False


class ShowIngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'amount', )


class UserSerializerModified(BaseUserSerializer):
    #is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    #def get_is_subscribed(self, obj):
    #    request = self.context.get('request')
    #    if request is None or request.user.is_anonymous:
    #        return False
    #    return Follow.objects.filter(user=request.user, author=obj).exists()


class ShowRecipeSerializer(FlagSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializerModified(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta(FlagSerializer.Meta):
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_ingredients(self, obj):
        qs = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(qs, many=True).data

    #def get_is_favorited(self, obj):
    #    request = self.context.get('request')
    #    if request is None or request.user.is_anonymous:
    #        return False
    #    user = request.user
    #    return Favorite.objects.filter(recipe=obj, user=user).exists()

    #def get_is_in_shopping_cart(self, obj):
    #    request = self.context.get('request')
    #    if request is None or request.user.is_anonymous:
    #        return False
    #    user = request.user
    #    return ShoppingList.objects.filter(recipe=obj, user=user).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    #id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    author = UserSerializerModified(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        for ingredient in ingredients_data:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингридиента должно быть больше нуля!')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            amount = ingredient['amount']
            #IngredientInRecipe.objects.create(
            #    ingredient=ingredient_model,
            #    recipe=recipe,
            #    amount=amount
            #)
            IngredientInRecipe.objects.bulk_create(
                ingredient_model,
                recipe,
                amount
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredient_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        for ingredient in ingredient_data:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингридиента должно быть больше нуля!')
        #IngredientInRecipe.objects.filter(recipe=instance).delete()
        IngredientInRecipe.objects.select_related('recipes_ingredients_list').delete()
        for new_ingredient in ingredient_data:
            IngredientInRecipe.objects.create(
                ingredient=Ingredient.objects.get(id=new_ingredient['id']),
                recipe=instance,
                amount=new_ingredient['amount']
            )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        instance.tags.set(tags_data)
        return instance

    def to_representation(self, instance):
        return ShowRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
