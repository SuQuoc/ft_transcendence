.PHONY: all up build_up build_no_cache down rm_vol re

all: up

up:
	docker compose --profile all up

build_up:
	docker compose --profile all up --build

build_no_cache:
	docker compose --profile all build --no-cache

down:
	docker compose --profile all down

rm_vol:
	docker volume prune -af

re: down rm_vol
	docker system prune -af
	docker compose --profile all up --build



###################### Registration #####################
.PHONY: registration_up registration_down

registration_up:
	@docker compose --profile registration build
	@docker compose --profile registration up

registration_down:
	@docker compose --profile registration down



###################### User Management #####################
.PHONY: user_management_up user_management_down mm migrate shell

user_management_up:
	@docker compose --profile user_management build
	@docker compose --profile user_management up

user_management_down:
	@docker compose --profile user_management down

mm:
	docker compose exec user_management python manage.py makemigrations

migrate:
	docker compose exec user_management python manage.py migrate

shell:
	docker compose exec user_management python manage.py shell

