
from django.shortcuts import redirect
from django.views import generic
from receipts.models import (
    Dish,
    Category,
    Restaurant,
    Shop
)
from community.models import Post
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


class DishCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dish


class PostListView(generic.ListView):
    model = Post
    queryset = Post.objects.all().order_by("-created_time")
    template_name = "receipts/dish_detail.html"


class PostCreateView(generic.CreateView):
    model = Post
    template_name = "receipts/dish_detail.html"


class PostDetailView(generic.DetailView):
    model = Post
    queryset = Post.objects.all().prefetch_related("comments")





class SendCommentView(LoginRequiredMixin, generic.View):
    model = Post
    fields = ["content"]

    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        comment = (Post.objects.
                   create(post=post, content=request.POST.get("content")))
        comment.save()
        return redirect("receipts:post-detail")


class RestaurantListView(generic.ListView):
    model = Restaurant
    paginate_by = 5
    template_name = "receipts/dish_detail.html"


class ShopListView(generic.ListView):
    model = Shop
    paginate_by = 5
    template_name = "receipts/dish_detail.html"
