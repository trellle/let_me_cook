from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class Currency(models.Model):
    name = models.CharField(max_length=10)
    rate_to_usdt = models.DecimalField(max_digits=10, decimal_places = 7)


class Achievement(models.Model):
    label = models.CharField(max_length=128)
    description = models.TextField(null=False, blank=True)
    pictogram = models.ImageField()
    fetch_time = models.DateTimeField()


class Cooker(AbstractUser):
    avatar = models.ImageField(null=True, blank=True)
    rank = models.CharField(max_length=128, default="Novice")
    achievements = models.ManyToManyField(Achievement, related_name="cookers")
    currency = models.ForeignKey(Currency,
                                 on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 related_name="person")
    friends = models.ManyToManyField("self", blank=True)

    
class Post(models.Model):
    author = models.ForeignKey(Cooker, on_delete=models.CASCADE, related_name="posts")
    created_time = models.DateTimeField(auto_now_add=True)
    dish = models.ForeignKey("receipts.Dish", on_delete=models.CASCADE, related_name="comments")
    rate = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    pros = models.TextField(blank=True, null=True)
    cons = models.TextField(blank=True, null=True)
    content = models.TextField()


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    media = models.ImageField(null=True, blank=True)


class Comment(models.Model):
    author = models.ForeignKey(Cooker, on_delete=models.CASCADE, related_name="comments")
    create_time = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
