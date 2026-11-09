from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("discover/", views.discover, name="discover"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("profile/<str:username>/follow/", views.toggle_follow, name="toggle_follow"),
    path("posts/create/", views.create_post, name="create_post"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("posts/<int:post_id>/comments/", views.add_comment, name="add_comment"),
    path(
        "comments/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
    path("posts/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        views.SiteLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]
