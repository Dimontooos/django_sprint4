from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.views.generic import ListView, DetailView

from .models import Post, Comment, Category
from .forms import PostForm, CommentForm, UserForm


class IndexView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "page_obj"
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now(),
        ).order_by("-pub_date")


class CategoryPostsView(ListView):
    model = Post
    template_name = "blog/category.html"
    context_object_name = "page_obj"
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        category = get_object_or_404(
            Category, slug=category_slug, is_published=True
        )
        return Post.objects.filter(
            category=category, pub_date__lte=now(), is_published=True
        ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(
            Category, slug=self.kwargs.get("category_slug")
        )
        return context


class AuthorPostsView(ListView):
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "page_obj"
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs.get("username")
        author = get_object_or_404(User, username=username)
        if self.request.user == author:
            return Post.objects.filter(author=author).order_by("-pub_date")
        return Post.objects.filter(
            author=author, is_published=True, pub_date__lte=now()
        ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User, username=self.kwargs.get("username")
        )
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
        context["comments"] = self.object.comments.select_related(
            "author", "post"
        ).order_by("created_at")
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
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
        return redirect("blog:profile", username=request.user.username)
    return redirect("blog:post_detail", pk=post_id)


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
    return render(
        request, "blog/post_detail.html", {"form": form, "post": post}
    )


@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, "blog/profile.html", {"profile": user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(
                "blog:profile", username=form.cleaned_data["username"]
            )  # Ensure 'auth' namespace is registered
    else:
        form = UserForm(instance=request.user)
    return render(
        request, "blog/user.html", {"form": form, "profile": request.user}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment, id=comment_id, post_id=post_id, author_id=request.user.id
    )
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", pk=post_id)
    return render(request, "blog/comment.html", {"comment": comment})


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment, id=comment_id, post_id=post_id, author_id=request.user.id
    )
    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", pk=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(
        request, "blog/comment.html", {"form": form, "comment": comment}
    )
