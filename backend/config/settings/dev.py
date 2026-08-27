"""Development settings."""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

INSTALLED_APPS = INSTALLED_APPS  # noqa: F405  (dev-only apps shu yerga qoʻshiladi)

# Dev'da CORS'ni kengroq ochish qulay, lekin baribir aniq origin'lar bilan.
CORS_ALLOWED_ORIGINS = env(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)
