"""Health-check (T-P1-56 skeleti)."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.http import JsonResponse


def healthz(request):
    """DB ulanishi + qoʻllanilmagan migration'larni tekshiradi → 200/503."""
    checks = {}
    ok = True

    # DB
    try:
        connection.ensure_connection()
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {exc}"
        ok = False

    # Migrations
    try:
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        checks["migrations"] = "ok" if not plan else f"pending: {len(plan)}"
        if plan:
            ok = False
    except Exception as exc:  # noqa: BLE001
        checks["migrations"] = f"error: {exc}"
        ok = False

    return JsonResponse(
        {"status": "ok" if ok else "degraded", "checks": checks},
        status=200 if ok else 503,
    )
