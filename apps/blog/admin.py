from django.contrib import admin

from apps.blog.models import Category, Comment, Post, Report, ReplayComment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "created_at", "is_active")
    list_filter = ("is_active", "category", "created_at")
    search_fields = ("title", "description", "author__username")
    list_select_related = ("author", "category")
    date_hierarchy = "created_at"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "id")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "author__username", "post__title")
    list_select_related = ("author", "post")


@admin.register(ReplayComment)
class ReplayCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "created_at")
    search_fields = ("text", "author__username", "post__title")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "reason", "status", "post", "comment", "created_at")
    list_filter = ("status", "reason", "created_at")
    search_fields = ("reporter__username", "post__title", "comment__text", "details")
    list_editable = ("status",)
    readonly_fields = ("reporter", "post", "comment", "reason", "details", "created_at")
    list_select_related = ("reporter", "post", "comment")
