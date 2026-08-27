from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = (
        "author_name",
        "stars",
        "source",
        "reviewed_at",
        "is_featured",
        "is_active",
        "order",
    )
    list_editable = ("is_featured", "is_active", "order")
    list_filter = ("source", "rating", "is_featured", "is_active")
    search_fields = ("author_name", "text")

    @admin.display(description="Reyting", ordering="rating")
    def stars(self, obj):
        return format_html(
            '<span style="color:#f2a65a">{}</span>', "★" * obj.rating + "☆" * (5 - obj.rating)
        )
