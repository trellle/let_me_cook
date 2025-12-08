from django.shortcuts import redirect, render
from django.views import generic
from receipts.models import (
    Dish,
    Category,
    Receipt,
    Restaurant,
    Shop
)
from receipts.forms import DishForm, ReceiptForm, ReceiptStepsFormSet
from community.models import Post
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(generic.TemplateView):
    template_name = "receipts/index.html"


class DishListView(generic.ListView):
    model = Dish
    template_name = "receipts/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dishes"] = Dish.objects.all()
        context["courses"] = Category.objects.values_list("course", flat=True).distinct()
        context["contents"] = Category.objects.values_list("contents", flat=True).distinct()
        context["cookings"] = Category.objects.values_list("cooking", flat=True).distinct()
        context["cuisines"] = Category.objects.values_list("type_of_cuisine", flat=True).distinct()
        context["difficulties"] = Dish.Difficulties.choices
        return context
    
    def get_queryset(self):
        queryset = Dish.objects.all()
        courses = self.request.GET.getlist("course")
        contents = self.request.GET.getlist("content")
        ingredients = self.request.GET.getlist("ingredient")
        not_ingredients = self.request.GET.getlist("not_ingredient")
        cookings = self.request.GET.getlist("cooking")
        cuisines = self.request.GET.getlist("cuisine")
        min_rate = self.request.GET.get("min_rate")
        max_rate = self.request.GET.get("max_rate")
        by_rate = self.request.GET.get("by_rate", "desc")
        by_time = self.request.GET.get("by_time")
        by_price = self.request.GET.get("by_price")
        if courses:
            queryset = queryset.filter(category__course__in=courses)
        if contents:
            queryset = queryset.filter(category__content__in=contents)
        if cookings:
            queryset = queryset.filter(category__cooking__in=cookings)
        if cuisines:
            queryset = queryset.filter(category__type_of_cuisine__in=cuisines)
        if min_rate:
            queryset = queryset.filter(avg_rate__gte=min_rate)
        if max_rate:
            queryset = queryset.filter(avg_rate__lte=max_rate)
        if ingredients:
            queryset = queryset.filter(receipt__ingredients__in=ingredients)
        if not_ingredients:
            queryset = queryset.exclude(receipt__ingredients__in=not_ingredients)
        ordering = []
        if by_rate == "asc":
            ordering.append("average_rate")
        else:
            ordering.append("-average_rate")
        if by_time == "old":
            ordering.append("created_at")
        elif by_time == "new":
            ordering.append("-created_at")
        if by_price == "cheap":
            ordering.append("price")
        elif by_price == "expensive":
            ordering.append("-price")
        queryset = queryset.order_by(*ordering)
        return queryset


class DishDetailView(generic.DetailView):
    model = Dish
    queryset = Dish.objects.all().select_related("author", "receipt").prefetch_related("liked_users")
    template_name = "receipts/dish.html"


class DishCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dish
    template_name = "receipts/create_dish.html"
    form_class = DishForm
    success_url = reverse_lazy("community:my_receipts")

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.authors.add(self.request.user)
        return response


class ReceiptCreateView(LoginRequiredMixin, generic.CreateView):
    model = Receipt
    form_class = ReceiptForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["steps_formset"] = ReceiptStepsFormSet(self.request.POST)
        else:
            context["steps_formset"] = ReceiptStepsFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        steps_formset = context["steps_formset"]
        if steps_formset.is_valid():
            receipt = form.save()
            steps = steps_formset.save()
            receipt.steps.set(steps)
            return super().form_valid(form)
        else:
            return self.form_invalid()


class DishReceiptCreateView(LoginRequiredMixin, generic.View):
    def get(self, request):
        return render(request, "receipts/create.html", {
            "dish_form": DishForm(),
            "receipt_form": ReceiptForm(),
        })

    def post(self, request):
        dish_form = DishForm(self.request.POST)
        receipt_form = ReceiptForm(self.request.POST)
        if dish_form.is_valid() and receipt_form.is_valid():
            dish = dish_form.save()
            dish.authors.add(self.request.user)
            receipt = receipt_form.save(commit=False)
            receipt.dish = dish  # OneToOne зв’язок
            receipt.save()
            return redirect("community:my_receipts")
        return render(
            request, "receipts/dish_create.html", {
                "dish_form": dish_form,
                "receipt_form": receipt_form
            }
        )
