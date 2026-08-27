from modeltranslation.translator import TranslationOptions, register

from apps.cases.models import CasePair


@register(CasePair)
class CasePairTR(TranslationOptions):
    fields = (
        "title",
        "slug",
        "caption",
        "treatment_summary",
        "duration_note",
        "meta_title",
        "meta_description",
    )
