from modeltranslation.translator import TranslationOptions, register

from apps.reviews.models import Review


@register(Review)
class ReviewTR(TranslationOptions):
    fields = ("text",)
