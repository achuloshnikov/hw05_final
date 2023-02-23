from django.contrib.auth import get_user_model
from django.db import models

from yatube.settings import REDUCTION_SYMB_NUM

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='наименование',
        max_length=200,
    )
    slug = models.SlugField(
        unique=True,
    )
    description = models.TextField(
        verbose_name='описание',
    )

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='группа',
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )
    text = models.TextField(verbose_name='текст')
    image = models.ImageField('картинка', upload_to='posts/', blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return self.text[:REDUCTION_SYMB_NUM]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
    )
    text = models.TextField(verbose_name='текст')
    created = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )

    def __str__(self) -> str:
        return self.text[:REDUCTION_SYMB_NUM]


class Follow(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
    )
