from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.gallery.models import GalleryImage


@admin.register(GalleryImage)
class GalleryImageAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("preview", "alt", "category", "order", "is_active")
    list_display_links = ("preview", "alt")
    list_editable = ("category", "order", "is_active")
    list_filter = ("category", "is_active")

    @admin.display(description="")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:56px;height:38px;border-radius:4px;object-fit:cover">',
                obj.image.url,
            )
        return "—"
