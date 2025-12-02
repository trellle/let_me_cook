from django import forms
from receipts.models import Dish, Receipt, Step, Ingredient, Equipment, IngredientAmount
from django.forms import modelformset_factory, inlineformset_factory


ReceiptStepsFormSet = modelformset_factory(Step, fields=("duration", "content", "template",), extra=1)
IngredientAmountFormSet = inlineformset_factory(
    Receipt,
    Ingredient,
    fields=["amount", "measure"]
)


class IngredientForm(forms.ModelForm):
    pass


class StepForm(forms.ModelForm):
    pass


class ReceiptForm(forms.ModelForm):
    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    class Meta:
        model = Receipt
        fields = ["equipment", "ingredients", "steps"]


class DishForm(forms.Models):
    class Meta:
        model = Dish
        fields = ["name", "authors", "description", "receipt", "price_usdt", "difficulty_rate"]
