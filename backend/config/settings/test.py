"""
Test sozlamalari.
DIQQAT: Postgres majburiy — ExclusionConstraint (btree_gist) va GIN trigram index
SQLite'da mavjud emas, shuning uchun ADR-007 testlari faqat Postgres'da maʼnoli.
"""

from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Media testlarda vaqtinchalik katalogga
MEDIA_ROOT = BASE_DIR / ".test-media"  # noqa: F405
