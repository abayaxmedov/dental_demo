from modeltranslation.translator import TranslationOptions, register

from apps.core.models import ClinicSettings, StatCounter, WorkingHours


@register(ClinicSettings)
class ClinicSettingsTR(TranslationOptions):
    fields = (
        "name",
        "tagline",
        "about_short",
        "address",
        "license_text",
        "default_meta_title",
        "default_meta_description",
    )


@register(WorkingHours)
class WorkingHoursTR(TranslationOptions):
    fields = ("note",)


@register(StatCounter)
class StatCounterTR(TranslationOptions):
    fields = ("label",)
