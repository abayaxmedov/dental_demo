"""Xizmatlar va narxlar admini."""

from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin, TabularInline

from apps.services.models import Faq, PriceItem, Service, ServiceCategory


class PriceItemInline(TabularInline):
    model = PriceItem
    extra = 0
    fields = ("title", "price_from", "price_to", "unit", "is_promo", "order", "is_active")


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("title", "slug", "order", "service_count")
    list_editable = ("order",)
    prepopulated_fields = {}
    ordering = ("order",)

    @admin.display(description="Xizmatlar soni")
    def service_count(self, obj):
        return obj.services.count()


@admin.register(Service)
class ServiceAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("title", "category", "duration_minutes", "is_featured", "is_active", "order")
    list_editable = ("is_featured", "is_active", "order")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("title", "excerpt")
    filter_horizontal = ("doctors",)
    inlines = [PriceItemInline]
    fieldsets = (
        (None, {"fields": ("category", "title", "slug", "excerpt", "body")}),
        (
            "Koʻrinish",
            {"fields": ("cover", "icon", "duration_minutes", "is_featured", "is_active", "order")},
        ),
        ("Shifokorlar", {"fields": ("doctors",)}),
        (
            "SEO",
            {"classes": ("collapse",), "fields": ("meta_title", "meta_description", "og_image")},
        ),
    )


@admin.register(PriceItem)
class PriceItemAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("title", "category", "price_display", "unit", "is_promo", "is_active", "order")
    list_editable = ("is_promo", "is_active", "order")
    list_filter = ("category", "is_promo", "is_active")
    search_fields = ("title",)

    @admin.display(description="Narx", ordering="price_from")
    def price_display(self, obj):
        base = f"{obj.price_from:,.0f}".replace(",", " ")
        if obj.price_to:
            return f"{base} – {obj.price_to:,.0f}".replace(",", " ") + f" {obj.currency}"
        return f"{base} {obj.currency}"


@admin.register(Faq)
class FaqAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("question", "service", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "service")
    search_fields = ("question", "answer")
