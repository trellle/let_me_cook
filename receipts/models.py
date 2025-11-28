from django.db import models
from community.models import Cooker
from django.core.validators import MinValueValidator, MaxValueValidator


class Equipment(models.Model):
    name = models.CharField(max_length=25)
    model = models.CharField(max_length=128, null=True, blank=True)
    category = models.CharField(max_length=128) # choice field
    amount = models.IntegerField()

    class Meta:
            constraints = [
                models.CheckConstraint(
                    check=models.Q(amount__gte=1),
                    name="amount_value_check"
                )
            ]


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
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="steps")
    duration = models.TimeField()
    content = models.TextField()
    template = models.ImageField(null=True, blank=True)


class IngredientsAmount(models.Model):
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    measure = models.CharField(max_length=128) # choice field


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
                                       validators=[
                                           MinValueValidator(0),
                                           MaxValueValidator(5)
                                       ])


class Category(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="category")
    course = models.CharField(max_length=256) # by role in eating
    content = models.CharField(max_length=256) # by composition
    cooking = models.CharField(max_length=256) # by cooking method
    type_of_cuisine = models.CharField(max_length=256) # cuisine from different countries


class Institution(models.Model):
    photo = models.ImageField()
    name = models.CharField(max_length=128)
    shedule = models.DateTimeField()
    country = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    address = models.CharField(max_length=256)


class Shop(Institution):
    assorti = models.ManyToManyField(Ingredient, related_name="shops")


class Restaurant(Institution):
    menu = models.ManyToManyField(Dish, related_name="restaurants")
