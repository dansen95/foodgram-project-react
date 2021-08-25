from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='email', max_length=255, unique=True)
    username = models.CharField(max_length=150,
                                verbose_name="username",
                                unique=True)
    first_name = models.CharField(max_length=150,
                                  verbose_name="first_name")
    last_name = models.CharField(max_length=150,
                                 verbose_name="last_name")

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь подписчик')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь на которого подписываемся')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow')]

    def __str__(self):
        return f'{self.user} => {self.author}'
