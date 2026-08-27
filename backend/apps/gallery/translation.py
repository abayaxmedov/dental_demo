from modeltranslation.translator import TranslationOptions, register

from apps.gallery.models import GalleryImage


@register(GalleryImage)
class GalleryImageTR(TranslationOptions):
    fields = ("alt", "caption")
