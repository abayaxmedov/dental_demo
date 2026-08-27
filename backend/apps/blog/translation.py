from modeltranslation.translator import TranslationOptions, register

from apps.blog.models import Post


@register(Post)
class PostTR(TranslationOptions):
    fields = ("title", "slug", "excerpt", "body", "meta_title", "meta_description")
