from django.db import models
from community.models import Cooker
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import time


class Equipment(models.Model):
    name = models.CharField(max_length=25)
    model = models.CharField(max_length=128, null=True, blank=True)
    category = models.CharField(max_length=128) # choice field
    amount = models.IntegerField(validators=[MinValueValidator(1)])


class IngredientCategory(models.Model):
    tag = models.CharField(max_length=256, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    categories = models.ManyToManyField(IngredientCategory, related_name="ingredient")
    calories_per_100g = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


class Receipt(models.Model):
    equipment = models.ManyToManyField(Equipment, related_name="receipt")
    ingredients = models.ManyToManyField(Ingredient, related_name="receipt", through="IngredientsAmount")


class Step(models.Model):
    def check_duration(value):
        if value <= time(0, 0, 0):
            raise ValidationError("Duration must be greater than 0.")

    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="steps")
    duration = models.TimeField(validators=[check_duration])
    content = models.TextField()
    template = models.ImageField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duration__gt="00:00:00"),
                name="duration_positive"
            )
        ]


class Measure(models.Model):
     name = models.CharField(max_length=64)
     abbreviation = models.CharField(max_length=32)
     info = models.TextField()
     image = models.ImageField()


class IngredientsAmount(models.Model):
    def check_amount(value):
        if value <= 0.0:
            raise ValidationError("Amount must be greater than 0.")

    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="ingredients_amount")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[check_amount])
    measure = models.ForeignKey(Measure, on_delete=models.PROTECT, related_name="ingredients_amount")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0.0),
                name="amount_positive"
            )
        ]


class Dish(models.Model):
    class Difficulties(models.TextChoices):
        ELEMENTARY = "super easy", "even kids can make"
        EASY = "easy", "everyone can repeat"
        NORMAL = "normal", "skilled"
        HARD = "hard", "nice cooker"
        PRO = "pro", "growing talent"
        CHEF = "chef", "cooking artist"

    name = models.CharField(max_length=512)
    authors = models.ManyToManyField(Cooker,
                               related_name="inventions")
    liked_users = models.ManyToManyField(Cooker, related_name="favourites")
    description = models.TextField(null=True, blank=True)
    receipt = models.OneToOneField(Receipt, on_delete=models.CASCADE, related_name="dish")
    price_usdt = models.DecimalField(max_digits=10, decimal_places=2)
    difficulty_rate = models.CharField(max_length=64, choices=Difficulties.choices) # choice field
    creation_time = models.DateTimeField(auto_now_add=True)
    average_rate = models.DecimalField(max_digits=10,
                                       decimal_places = 2,
                                       null=True,
                                       validators=[
                                           MinValueValidator(0),
                                           MaxValueValidator(5)
                                       ])


class CookingMethod(models.Model):
    name = models.CharField(max_length=64)


class Cuisine(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()


class Category(models.Model):
    class CourseChoices(models.TextChoices):
        MAIN = "main", "main course"
        SOUP = "soup", "first course"
        SALAD = "salad", "salads"
        DESERT = "desert", "sweet deserts"
        DRINK = "drink", "drinks"
        SAUCE = "sauce", "spices&sauces"
        SNACK = "snack", "starters"
        BAKERY = "bakery", "baked goods"
        SIDE_DISH = "side dish", "darnish"
        BREAKFAST = "breakfast", "morning meals"

    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="category")
    course = models.CharField(max_length=256, choices=CourseChoices.choices) # by role in eating
    cooking = models.ManyToManyField(CookingMethod, related_name="dish_category") # by cooking method
    type_of_cuisine = models.ForeignKey(Cuisine, on_delete=models.SET_NULL, null=True, related_name="dish_category") # cuisine from different countries


class Institution(models.Model):
    photo = models.ImageField(null=True)
    name = models.CharField(max_length=128)
    shedule = models.DateTimeField()
    country = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    address = models.CharField(max_length=256)


class Shop(Institution):
    assorti = models.ManyToManyField(Ingredient, related_name="shops")


class Restaurant(Institution):
    menu = models.ManyToManyField(Dish, related_name="restaurants")
