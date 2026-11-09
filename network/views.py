from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CommentForm, LoginForm, PostForm, ProfileForm, RegisterForm
from .models import Comment, Follow, Post, Profile


POSTS_PER_PAGE = 8
USERS_PER_PAGE = 12


def _safe_return(request, fallback):
    target = request.POST.get("next", "")
    if target and url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(target)
    return redirect(fallback)


def _posts_with_counts():
    return (
        Post.objects.select_related("author", "author__profile")
        .annotate(
            likes_total=Count("likes", distinct=True),
            comments_total=Count("comments", distinct=True),
        )
        .order_by("-created_at")
    )


def _mark_likes(request, target):
    posts = list(target.object_list if hasattr(target, "object_list") else target)
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            request.user.liked_posts.filter(pk__in=[post.pk for post in posts])
            .values_list("pk", flat=True)
        )
    for post in posts:
        post.is_liked = post.pk in liked_ids
    return target


def home(request):
    page_obj = Paginator(_posts_with_counts(), POSTS_PER_PAGE).get_page(
        request.GET.get("page")
    )
    _mark_likes(request, page_obj)
    return render(
        request,
        "network/home.html",
        {"page_obj": page_obj, "post_form": PostForm()},
    )


def discover(request):
    query = request.GET.get("q", "").strip()[:60]
    people = User.objects.all().annotate(
        posts_total=Count("posts", distinct=True),
        followers_total=Count("followers", distinct=True),
        following_total=Count("following", distinct=True),
    )
    if request.user.is_authenticated:
        people = people.exclude(pk=request.user.pk)
    if query:
        people = people.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query)
        )
    people = people.order_by("-date_joined", "username")
    page_obj = Paginator(people, USERS_PER_PAGE).get_page(request.GET.get("page"))

    following_ids = set()
    if request.user.is_authenticated:
        following_ids = set(
            Follow.objects.filter(
                follower=request.user, following__in=page_obj.object_list
            ).values_list("following_id", flat=True)
        )
    for person in page_obj.object_list:
        person.is_followed = person.pk in following_ids
    return render(
        request,
        "network/discover.html",
        {"page_obj": page_obj, "query": query},
    )


def profile(request, username):
    person = get_object_or_404(User, username=username)
    person_profile, _ = Profile.objects.get_or_create(user=person)
    page_obj = Paginator(
        _posts_with_counts().filter(author=person), POSTS_PER_PAGE
    ).get_page(request.GET.get("page"))
    _mark_likes(request, page_obj)
    is_following = request.user.is_authenticated and Follow.objects.filter(
        follower=request.user, following=person
    ).exists()
    return render(
        request,
        "network/profile.html",
        {
            "person": person,
            "person_profile": person_profile,
            "page_obj": page_obj,
            "followers_total": person.followers.count(),
            "following_total": person.following.count(),
            "is_following": is_following,
        },
    )


@login_required
def edit_profile(request):
    person_profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=person_profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile", username=request.user.username)
    return render(request, "network/edit_profile.html", {"form": form})


@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, "Your post is live.")
    else:
        messages.error(request, "Please enter a post of 1 to 500 characters.")
    return _safe_return(request, "home")


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    post.delete()
    messages.success(request, "Your post has been deleted.")
    return _safe_return(request, "home")


def post_detail(request, post_id):
    post = get_object_or_404(
        _posts_with_counts().select_related("author__profile"), pk=post_id
    )
    _mark_likes(request, [post])
    comments = post.comments.select_related("author", "author__profile")
    return render(
        request,
        "network/post_detail.html",
        {"post": post, "comments": comments, "comment_form": CommentForm()},
    )


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        messages.success(request, "Your comment has been added.")
    else:
        messages.error(request, "Please enter a comment of 1 to 280 characters.")
    return _safe_return(request, reverse("post_detail", args=[post_id]))


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    post_id = comment.post_id
    comment.delete()
    messages.success(request, "Your comment has been deleted.")
    return _safe_return(request, reverse("post_detail", args=[post_id]))


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.likes.filter(pk=request.user.pk).exists():
        post.likes.remove(request.user)
        messages.info(request, "You removed your like.")
    else:
        post.likes.add(request.user)
        messages.success(request, "You liked the post.")
    return _safe_return(request, "home")


@login_required
@require_POST
def toggle_follow(request, username):
    person = get_object_or_404(User, username=username)
    if person.pk == request.user.pk:
        messages.error(request, "You cannot follow your own account.")
        return _safe_return(request, reverse("profile", args=[username]))

    follow, created = Follow.objects.get_or_create(
        follower=request.user, following=person
    )
    if created:
        messages.success(request, f"You are now following @{person.username}.")
    else:
        follow.delete()
        messages.info(request, f"You unfollowed @{person.username}.")
    return _safe_return(request, reverse("profile", args=[username]))


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to your new community.")
        return redirect("home")
    return render(request, "registration/register.html", {"form": form})


class SiteLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm

    def form_valid(self, form):
        messages.success(self.request, "Welcome back.")
        return super().form_valid(form)


