from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from django.conf import settings


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Ник',
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )

    class Meta:
        ordering = ('username',)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Follower(models.Model):
    followed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE
    )
    following_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='followers',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('-followed_user',)
        unique_together = [['followed_user', 'following_user']]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def save(self, *args, **kwargs):
        if self.followed_user == self.following_user:
            raise ValidationError('Нельзя подписаться на самого себя')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.followed_user} follows {self.following_user}'
