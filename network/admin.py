from django.contrib import admin

from .models import Comment, Follow, Post, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
    search_fields = ("user__username", "bio")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at", "likes_count")
    list_filter = ("created_at",)
    search_fields = ("author__username", "body")
    readonly_fields = ("created_at",)

    @admin.display(description="Likes")
    def likes_count(self, obj):
        return obj.likes.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "created_at")
    search_fields = ("author__username", "body")
    readonly_fields = ("created_at",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
