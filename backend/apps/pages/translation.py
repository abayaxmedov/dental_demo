from modeltranslation.translator import TranslationOptions, register

from apps.pages.models import StaticPage


@register(StaticPage)
class StaticPageTR(TranslationOptions):
    fields = ("title", "body", "meta_title", "meta_description")
