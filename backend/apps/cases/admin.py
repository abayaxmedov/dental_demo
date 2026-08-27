"""Before/After ishlar admini."""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.cases.models import CasePair


@admin.register(CasePair)
class CasePairAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = (
        "preview",
        "title",
        "service",
        "doctor",
        "consent_on_file",
        "is_published",
        "is_featured",
        "order",
    )
    list_display_links = ("preview", "title")
    list_editable = ("is_published", "is_featured", "order")
    list_filter = ("is_published", "is_featured", "consent_on_file", "service")
    search_fields = ("title", "caption")
    autocomplete_fields = ("service", "doctor")

    @admin.display(description="")
    def preview(self, obj):
        if obj.image_after:
            return format_html(
                '<img src="{}" style="width:56px;height:38px;border-radius:4px;object-fit:cover">',
                obj.image_after.url,
            )
        return "—"
