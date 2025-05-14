from django.urls import path

from . import views
from .views import (
    IndexView,
    CategoryPostsView,
    AuthorPostsView,
    PostDetailView,
)

app_name = "blog"

urlpatterns = [
    path("posts/create/", views.create_post, name="create_post"),
    path("posts/<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path(
        "posts/<int:post_id>/comment/", views.add_comment, name="add_comment"
    ),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("", IndexView.as_view(), name="index"),
    path(
        "category/<slug:category_slug>/",
        CategoryPostsView.as_view(),
        name="category_posts",
    ),
    path("profile/<str:username>/", AuthorPostsView.as_view(), name="profile"),
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),
]
