from django import forms
from receipts.models import Dish


class DishCreate(forms.Models):
    class Meta:
        model = Dish
        fields = []
