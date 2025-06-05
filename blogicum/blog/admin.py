from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode


from .models import Category, Location, Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "preview",
        "is_published",
        "location",
        "category",
        "author",
        "all_comments",
    )
    list_editable = ("is_published",)
    search_fields = ("title",)
    list_filter = (
        "category",
        "location",
    )
    list_display_links = ("title",)
    readonly_fields = ["preview"]

    @admin.display(description="Миниатюра", empty_value="Нет фото")
    def preview(self, object):
        if object.image:
            return mark_safe(
                f'<img src="{object.image.url}" style="max-height: 100px;">'
            )

    @admin.display(description="Комментарии", empty_value="Нет комментариев")
    def all_comments(self, object):
        count = object.comments.count()
        if count:
            url = (
                reverse("admin:blog_comment_changelist")
                + "?"
                + urlencode({"post__id": f"{object.id}"})
            )
            return format_html(
                '<a href="{}"> Комментариев: ({})</a>', url, count
            )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "author")
    search_fields = ("text__startswith",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "slug",
        "is_published",
    )
    list_editable = ("is_published",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name",)
