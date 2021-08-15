from datetime import date

import django_filters.rest_framework
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import (CustomUser, Favorite, Ingredient,
                     IngredientInRecipe, Recipe, ShoppingList, Tag)
from users.models import Follow
from .paginators import PageNumberPaginatorModified
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer,
                          IngredientSerializer, ListRecipeSerializer,
                          ShowFollowersSerializer, TagSerializer,
                          FollowSerializer, FavoriteSerializer,
                          ShoppingListSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filter_class = RecipeFilter
    pagination_class = PageNumberPaginatorModified
    permission_classes = [AdminOrAuthorOrReadOnly, ]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ListRecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def showfollows(request):
    user_obj = CustomUser.objects.filter(following__user=request.user)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(user_obj, request)
    serializer = ShowFollowersSerializer(
        result_page, many=True, context={'current_user': request.user})
    return paginator.get_paginated_response(serializer.data)


class FollowView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, author_id):
        user = request.user

        data = {
            'user': user.id,
            'author': author_id
        }
        serializer = FollowSerializer(data=data, context={'request': request})

        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        user = request.user
        author = get_object_or_404(CustomUser, id=author_id)
        obj = get_object_or_404(Follow, user=user, author=author)
        obj.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class FavouriteView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }
        serializer = FavoriteSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid()
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj = get_object_or_404(Favorite, user=user, recipe=recipe)
        obj.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )



class ShoppingListView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, recipe_id):
        user = request.user
        data = {
            'user': user.id,
            'recipe': recipe_id,
        }

        context = {'request': request}
        serializer = ShoppingListSerializer(data=data, context=context)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj = get_object_or_404(ShoppingList, user=user, recipe=recipe)
        obj.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class DownloadShoppingCart(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        buying_list = {}
        ingredients = IngredientInRecipe.objects.filter(
            recipe__purchases__user=request.user
        )
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in buying_list:
                buying_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                buying_list[name]['amount'] += amount

        wishlist = []
        for item in buying_list:
            wishlist.append(f'{item} - {buying_list[item]["amount"]} '
                            f'{buying_list[item]["measurement_unit"]} \n')
        wishlist.append('\n')
        today = date.today()
        wishlist.append(f'FoodGram, {today.year}')
        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
