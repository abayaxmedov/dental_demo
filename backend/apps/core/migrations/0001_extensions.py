"""
Postgres extension'lari (T-P1-04). Bularsiz:
- btree_gist  → Appointment ExclusionConstraint ishlamaydi (ADR-007)
- pg_trgm     → blog qidiruvi uchun GIN trigram index ishlamaydi
- unaccent    → diakritiksiz qidiruv
"""
from django.contrib.postgres.operations import (
    BtreeGistExtension,
    TrigramExtension,
    UnaccentExtension,
)
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        BtreeGistExtension(),
        TrigramExtension(),
        UnaccentExtension(),
    ]
