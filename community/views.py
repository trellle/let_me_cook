from django.shortcuts import render
from django.views import generic
from community.models import Post, Comment
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin


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


class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Post


class SendCommentView(LoginRequiredMixin, generic.View):
    model = Comment
    fields = ["message"]

    def post(self, request, pk):
        post = Post.objects.get(id=pk)
        comment = (Post.objects.
                   create(post=post, content=request.POST.get("content")))
        comment.save()
        return redirect("receipts:post-detail")


class DeleteCommentView(LoginRequiredMixin, generic.DeleteView):
    model = Comment
