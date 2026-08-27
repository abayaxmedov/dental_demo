"""IntegrityError sabablarini ajratish (psycopg 3 .diag orqali, str(exc) parse QILINMAYDI)."""

UNIQUE_VIOLATION = "23505"
EXCLUSION_VIOLATION = "23P01"
CHECK_VIOLATION = "23514"
FK_VIOLATION = "23503"
NOT_NULL_VIOLATION = "23502"


def constraint_of(exc: Exception) -> tuple[str | None, str]:
    """(sqlstate, constraint_name) — Django IntegrityError'ni psycopg cause'iga qarab."""
    cause = getattr(exc, "__cause__", None)
    diag = getattr(cause, "diag", None)
    return getattr(cause, "sqlstate", None), (getattr(diag, "constraint_name", None) or "")
