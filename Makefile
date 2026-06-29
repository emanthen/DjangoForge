.PHONY: dev build test lint format migrate migrations shell superuser seed logs down

dev:
	docker compose up

build:
	docker compose build

test:
	docker compose run --rm web pytest --tb=short

lint:
	docker compose run --rm web ruff check .

format:
	docker compose run --rm web ruff format .

migrate:
	docker compose run --rm web python manage.py migrate

migrations:
	docker compose run --rm web python manage.py makemigrations

shell:
	docker compose run --rm web python manage.py shell

superuser:
	docker compose run --rm web python manage.py createsuperuser

seed:
	docker compose run --rm web python manage.py seed_data

logs:
	docker compose logs -f web

down:
	docker compose down

check:
	docker compose run --rm web python manage.py check --deploy

coverage:
	docker compose run --rm web coverage run -m pytest && docker compose run --rm web coverage report

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
