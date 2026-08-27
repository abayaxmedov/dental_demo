from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.blog.models import Post


@admin.register(Post)
class PostAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("title", "author", "published_at", "reading_time", "is_published")
    list_editable = ("is_published",)
    list_filter = ("is_published", "author")
    search_fields = ("title", "excerpt", "body")
    date_hierarchy = "published_at"
    autocomplete_fields = ("author",)
    readonly_fields = ("reading_time",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "excerpt", "body")}),
        ("Nashr", {"fields": ("cover", "author", "published_at", "is_published", "reading_time")}),
        (
            "SEO",
            {"classes": ("collapse",), "fields": ("meta_title", "meta_description", "og_image")},
        ),
    )
