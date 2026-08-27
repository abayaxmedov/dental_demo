from modeltranslation.translator import TranslationOptions, register

from apps.team.models import Doctor, TimeOff


@register(Doctor)
class DoctorTR(TranslationOptions):
    fields = (
        "full_name",
        "slug",
        "specialization",
        "bio",
        "photo_alt",
        "education",
        "certificates",
        "meta_title",
        "meta_description",
    )


@register(TimeOff)
class TimeOffTR(TranslationOptions):
    fields = ("reason",)
