from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin

from apps.pages.models import StaticPage


@admin.register(StaticPage)
class StaticPageAdmin(TabbedTranslationAdmin, ModelAdmin):
    list_display = ("title", "key", "is_active")
    list_filter = ("is_active",)
