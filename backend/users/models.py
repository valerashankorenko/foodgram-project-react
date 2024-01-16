from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, ValidationError
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя.
    """
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,)
    username = models.CharField(
        'Уникальный юзернейм',
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+$')],
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    is_subscribed = models.BooleanField(
        'Подписка',
        default=False)
    password = models.CharField(
        'Пароль',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    """Модель для подписки."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='followed',
        on_delete=models.CASCADE,
        verbose_name='автор'
    )

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Пользователь не может подписаться на самого себя.')
        if Subscription.objects.filter(user=self.user,
                                       author=self.author).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'author')
        ordering = ('user', )
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (f'Автор {self.author.username}, '
                f'подписчик {self.user.username}')
