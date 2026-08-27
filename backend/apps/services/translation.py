from modeltranslation.translator import TranslationOptions, register

from apps.services.models import Faq, PriceItem, Service, ServiceCategory


@register(ServiceCategory)
class ServiceCategoryTR(TranslationOptions):
    fields = ("title", "slug")


@register(Service)
class ServiceTR(TranslationOptions):
    fields = ("title", "slug", "excerpt", "body", "meta_title", "meta_description")


@register(PriceItem)
class PriceItemTR(TranslationOptions):
    fields = ("title", "unit", "qualifier", "promo_note")


@register(Faq)
class FaqTR(TranslationOptions):
    fields = ("question", "answer")
