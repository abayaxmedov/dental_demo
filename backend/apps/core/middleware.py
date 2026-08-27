"""Til va admin lokalizatsiyasi middleware'lari."""

from django.utils import translation

from config.settings.base import LANGUAGES

SUPPORTED = {code for code, _ in LANGUAGES}


class AdminLocaleMiddleware:
    """
    /admin/ ichida interfeys doim oʻzbekcha — klinika xodimi uchun (R-14).
    API (/api/) esa Accept-Language / ?lang= ni hurmat qiladi.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            with translation.override("uz"):
                return self.get_response(request)
        return self.get_response(request)


class QueryParamLocaleMiddleware:
    """
    `?lang=ru` query parametri Accept-Language'dan ustun turadi (ADR E-qism).
    LocaleMiddleware'dan KEYIN turishi kerak.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get("lang")
        if lang in SUPPORTED:
            with translation.override(lang):
                request.LANGUAGE_CODE = lang
                return self.get_response(request)
        return self.get_response(request)
