from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True, blank=False)
    username = models.TextField(
        max_length=150,
        unique=True,
        blank=False
    )
    first_name = models.TextField(max_length=150, blank=False)
    last_name = models.TextField(max_length=150, blank=False)
    password = models.TextField(max_length=150, blank=False)
    # shopping_cart = models.ForeignKey(ShoppingCart,
    #                                   on_delete=models.CASCADE)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    def __str__(self):
        return self.username


class Follow(models.Model):
    """ Модель подписки на автора. """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f"{self.user} подписан на {self.author}"
