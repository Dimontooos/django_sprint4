from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.views.generic import ListView, DetailView
from django.http import HttpResponseForbidden

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm, UserForm


def paginate_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


class IndexView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "page_obj"

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now(),
        ).annotate(comment_count=Count('comments')).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        full_qs = self.get_queryset()
        context["page_obj"] = paginate_queryset(self.request, full_qs, per_page=10)
        return context


class CategoryPostsView(ListView):
    model = Post
    template_name = "blog/category.html"
    context_object_name = "page_obj"

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        category = get_object_or_404(Category, slug=category_slug, is_published=True)
        return Post.objects.filter(
            category=category,
            pub_date__lte=now(),
            is_published=True,
        ).annotate(comment_count=Count('comments')).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(Category, slug=self.kwargs.get("category_slug"))
        full_qs = self.get_queryset()
        context["page_obj"] = paginate_queryset(self.request, full_qs, per_page=10)
        return context


class AuthorPostsView(ListView):
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "page_obj"

    def get_queryset(self):
        username = self.kwargs.get("username")
        author = get_object_or_404(User, username=username)
        base_qs = Post.objects.filter(author=author)
        if self.request.user != author:
            base_qs = base_qs.filter(is_published=True, pub_date__lte=now())
        return base_qs.annotate(comment_count=Count('comments')).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(User, username=self.kwargs.get("username"))
        full_qs = self.get_queryset()
        context["page_obj"] = paginate_queryset(self.request, full_qs, per_page=10)
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        if (
            not post.is_published
            or not post.category.is_published
            or post.pub_date > now()
        ) and post.author != self.request.user:
            raise Http404("Post not found.")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author").order_by("created_at")
        return context


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm()
    return render(request, "blog/create.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", pk=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", pk=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, "blog/create.html", {"form": form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/detail.html", {"post": post, "is_delete": True})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("blog:post_detail", pk=post_id)
    else:
        form = CommentForm()
    return render(request, "blog/post_detail.html", {"form": form, "post": post})


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id, author=request.user)
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", pk=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, "blog/comment.html", {"form": form, "comment": comment})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id, author=request.user)
    if comment.author != request.user:
        return HttpResponseForbidden("Неовзожно удалить комментарий, автором которого вы не являетесь!.")
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", pk=post_id)
    return render(request, "blog/comment.html", {"comment": comment})

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "blog/profile.html", {"profile": user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=form.cleaned_data["username"])
    else:
        form = UserForm(instance=request.user)
    return render(request, "blog/user.html", {"form": form, "profile": request.user})