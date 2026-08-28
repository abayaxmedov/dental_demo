# dental_demo — monorepo Makefile (ADR-016)
# backend/ = Django DRF · frontend/ = Next.js
PY := backend/.venv/bin/python

.PHONY: help
help:
	@echo "dental_demo — buyruqlar:"
	@echo "  make db-up         # PostgreSQL 17 (docker) ishga tushirish"
	@echo "  make db-down       # DB toʻxtatish"
	@echo "  make be-install    # backend venv + requirements"
	@echo "  make be-migrate    # migration'larni qoʻllash"
	@echo "  make be-run        # Django dev server (:8000)"
	@echo "  make be-check      # django check"
	@echo "  make be-lint       # ruff"
	@echo "  make be-test       # pytest"
	@echo "  make reskin CONFIG=prospect.yml [ARGS=--dry-run]  # prospekt uchun qayta brendlash (ADR-012)"
	@echo "  make be-schema     # OpenAPI schema.yml generatsiya"
	@echo "  make fe-install    # frontend npm install"
	@echo "  make fe-run        # Next.js dev server (:3000)"
	@echo "  make fe-build      # Next.js production build"
	@echo "  make fe-test       # typecheck + rang lint + i18n kalit parity"
	@echo "  make fe-types      # OpenAPI'dan TS tiplar (backend ishga tushgan boʻlsin)"

# --- infra ---
db-up:
	docker-compose up -d db
db-down:
	docker-compose down

# --- backend ---
be-install:
	python3 -m venv backend/.venv && $(PY) -m pip install -U pip && $(PY) -m pip install -r backend/requirements.txt
be-migrate:
	cd backend && .venv/bin/python manage.py migrate
be-run:
	cd backend && .venv/bin/python manage.py runserver 0.0.0.0:8000
be-check:
	cd backend && .venv/bin/python manage.py check
be-lint:
	cd backend && .venv/bin/python -m ruff check . || true
be-test:
	cd backend && .venv/bin/python manage.py check_asset_licenses
	cd backend && .venv/bin/python -m pytest || true
be-schema:
	cd backend && .venv/bin/python manage.py spectacular --file schema.yml
# $(abspath …) SHART: retsept `cd backend` qiladi, shuning uchun repo ildizidan berilgan
# nisbiy yoʻl aks holda buziladi (AUDIT-2026-08-29 / T-FIX-03).
reskin:
	@test -n "$(CONFIG)" || { echo "Ishlatish: make reskin CONFIG=prospect.yml [ARGS=--dry-run]"; exit 2; }
	@test -f "$(CONFIG)" || { echo "Config topilmadi: $(CONFIG)"; exit 2; }
	cd backend && .venv/bin/python manage.py reskin --config "$(abspath $(CONFIG))" $(ARGS)

# --- frontend ---
fe-install:
	cd frontend && npm install
fe-run:
	cd frontend && npm run dev
fe-build:
	cd frontend && npm run build
fe-test:
	cd frontend && npm run test
fe-types:
	cd frontend && npx openapi-typescript http://localhost:8000/api/v1/schema/ -o src/lib/api-types.ts
