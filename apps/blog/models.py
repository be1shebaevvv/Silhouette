from django.db import models
from apps.accounts.models import User

# Create your models here.
from django.shortcuts import render

# # Podpiska
# class Subscription(models.Model):
#     subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
#     subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')
#     created_at = models.DateTimeField(auto_now_add=True)



class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField(max_length=150)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    title = models.CharField(verbose_name="Название", max_length=100)
    description = models.TextField("Описание")
    # image = models.ImageField("Фото", upload_to="posts/images/")
    media = models.FileField("Медия", upload_to='media/post_media')


    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    # выставит время во время создание записи
    created_at = models.DateTimeField(auto_now_add=True) 
    
    # Выставит время во время повторного обновления данных
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField("Активный", default=True)

    likes = models.ManyToManyField(User, related_name='liked_posts')
    dislikes = models.ManyToManyField(User, related_name='disliked_posts')
    chats = models.ManyToManyField(User, related_name="chats")

    class Meta: 
        verbose_name = "Пост"
        verbose_name_plural = "Посты"



class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comments")
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"

    @property
    def comment_set(self):
        return self.comments.order_by('-created_at')
    
    def __str__(self):
        return f"{self.text}"
    

class ReplayComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replay_comment')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_replay_comments')
    parent = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
    
    def __str__(self):
        return f"{self.text}"