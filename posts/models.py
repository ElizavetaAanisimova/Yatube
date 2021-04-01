from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название', max_length=200,
        help_text='Дайте название группе'
    )
    slug = models.SlugField(
        verbose_name='Слаг', unique=True,
        help_text='Укажите адрес для страницы'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Расскажите об интересах группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст публикации',
        help_text='Введите текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='posts'
    )
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL,
        verbose_name='Название группы',
        help_text='Выберите название группы',
        blank=True, null=True, related_name='posts'
    )
    image = models.ImageField(
        upload_to='posts/',
        verbose_name='Изображение',
        help_text='Выберите изображение',
        blank=True, null=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='comments'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_followings'
            )
        ]
