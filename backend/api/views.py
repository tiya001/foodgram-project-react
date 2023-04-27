from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.pagination import CustomPagination
from recipes.models import (FavoriteRecipes, Ingredient, IngredientInRecipe,
                            Recipe, ShoppingCart, Tag)
from users.models import CustomUser, Follow

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorPermission
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          PostPatchRecipeSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscribeListSerializer,
                          TagSerializer, UserSerializer)
from django.db.models import Sum


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter, )
    search_fields = ['^name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorPermission, IsAuthenticatedOrReadOnly)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return PostPatchRecipeSerializer

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        permission_classes=[IsAuthenticated]
        )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            context = {'request': request}
            recipe = get_object_or_404(Recipe, id=pk)
            data = {
                'user': request.user.id,
                'recipe': recipe.id
            }
            serializer = ShoppingCartSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = ShoppingCartSerializer(data=data, context=context)
        if ShoppingCart.objects.filter(user=data['user'],
                                       recipe=data['recipe']).exists():
            ShoppingCart.objects.get(user=data['user'],
                                     recipe=data['recipe']).delete()
            return Response(
                    {'status': 'Рецепт успешно удален из списка покупок'},
                    status=status.HTTP_200_OK,
                )
        return Response(
                {'status': 'Рецепта не было в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST,
                )

    @action(
        methods=['GET'],
        detail=False,
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_list__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = 'Cписок покупок:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        )
    def favorite(self, request, pk):
        if request.method == 'POST':
            context = {'request': request}
            recipe = get_object_or_404(Recipe, id=pk)
            data = {
                'user': request.user.id,
                'recipe': recipe.id
            }
            serializer = FavoriteSerializer(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = FavoriteSerializer(data=data, context=context)
        if FavoriteRecipes.objects.filter(user=data['user'],
                                          recipe=data['recipe']).exists():
            FavoriteRecipes.objects.get(user=data['user'],
                                        recipe=data['recipe']).delete()
            return Response(
                {'status': 'Рецепт успешно удален из списка избранных'},
                status=status.HTTP_200_OK,
                )
        return Response(
            {'status': 'Рецепта не было в списке избранных'},
            status=status.HTTP_400_BAD_REQUEST,
            )


class UserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, pk=id)

        if request.method == 'POST':
            serializer = SubscribeListSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return None

    @action(detail=False,
            )
    def subscriptions(self, request):
        user = request.user
        queryset = CustomUser.objects.filter(
            following__user=user).order_by('username')
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
