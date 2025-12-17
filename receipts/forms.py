from django import forms
from receipts.models import Dish, Receipt, Step, Ingredient, Equipment, Category, CookingMethod
from community.models import Cooker
from django.forms import modelformset_factory, inlineformset_factory
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget


ReceiptStepsFormSet = modelformset_factory(Step, fields=("duration", "content", "template",), extra=1)
IngredientAmountFormSet = inlineformset_factory(
    Receipt,
    Ingredient,
    fields=["ingredients", "amount", "measure"]
)


class IngredientSelect2Widget(forms.ModelForm):
    model = Ingredient
    search_fields = ["name_icontains"]


class IngredientForm(forms.ModelForm):
    name = forms.CharField(max_length=128, required=True)
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=Select2MultipleWidget,
        required=False
    )
    calories_per_100g = forms.FloatField(decimal_places=2, required=False)

    class Meta:
        model = Ingredient
        fields = ["name", "categories", "calories_per_100g"]


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ["duration", "template", "content"]


class EquipmentSelect2Widget(ModelSelect2MultipleWidget):
    model = Equipment
    search_fields = ["name_icontains"]


class ReceiptForm(forms.ModelForm):
    equipment = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=EquipmentSelect2Widget,
        required=True
    )
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Equipment.objects.all(),
        widget=IngredientSelect2Widget,
        required=True
    )
    class Meta:
        model = Receipt
        fields = ["equipment", "ingredients", "steps"]


class AuthorSelect2Widget(ModelSelect2MultipleWidget):
    model = Cooker
    search_fields = ["username_icontains"]


class CookingMethod2Widget(ModelSelect2MultipleWidget):
    model = CookingMethod
    search_fields = ["name_icontains"]


class CategoryForm(forms.ModelForm):
    course = forms.ChoiceField(
        choices=Category.CourseChoices,
        widget=forms.RadioSelect
    )
    cooking = forms.ModelMultipleChoiceField(
        queryset=CookingMethod.objects.all(),
        widget=CookingMethod2Widget,
        required=True
    )
    class Meta:
        model = Category
        fields = ["course", "cooking", "type_of_cuisine"]


class DishForm(forms.ModelForm):
    autors = forms.ModelMultipleChoiceField(
        queryset=Cooker.objects.all(),
        widget=AuthorSelect2Widget,
        required=False
    )
    class Meta:
        model = Dish
        fields = ["name", "authors", "description", "category", "receipt", "price_usdt", "difficulty_rate"]
