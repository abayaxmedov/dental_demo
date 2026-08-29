# dental_demo backend — Django + gunicorn (ADR-021).
# Python 3.14: .python-version bilan bir xil. psycopg[binary]/Pillow manylinux wheel'lari
# borligi uchun build toolsiz slim yetarli.
FROM python:3.14-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

# curl — healthcheck uchun (compose'da ishlatiladi).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Static build vaqtida bir marta yig'iladi (WhiteNoise manifest + siqish). DB kerak emas —
# faqat settings import'i uchun minimal dummy env. Runtime qiymatlari compose'dan keladi.
RUN SECRET_KEY=build-only DEBUG=False ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

RUN chmod +x docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
# 3 worker — kichik VPS uchun mos (2*CPU+1 taxminan). Timeout uzunroq: rasm yuklash.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", \
     "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
