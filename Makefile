DOCKER_COMPOSE = docker compose -f ./docker_compose_files/docker-compose.yml



###################### General #####################
.PHONY: all up build_up build_no_cache down rm_vol clean fclean re new

all: up

up:
	${DOCKER_COMPOSE} --profile all up

build_up:
	${DOCKER_COMPOSE} --profile all up --build

build_no_cache:
	${DOCKER_COMPOSE} --profile all build --no-cache

down:
	${DOCKER_COMPOSE} --profile all down

rm_vol:
	docker volume prune -af

clean: down
	docker system prune -f

fclean: down rm_vol
	docker system prune -af

re: down rm_vol build_up

new: fclean build_up

keys:
	bash ./src/common_files/jwt_create_keys.sh

###################### Registration #####################
.PHONY: registration_up registration_down

registration_up:
	@${DOCKER_COMPOSE} --profile registration build
	@${DOCKER_COMPOSE} --profile registration up

registration_down:
	@${DOCKER_COMPOSE} --profile registration down



###################### User Management #####################
.PHONY: um_up um_down um_mm um_migrate um_shell

um_up:
	@${DOCKER_COMPOSE} --profile user_management build
	@${DOCKER_COMPOSE} --profile user_management up

um_down:
	@${DOCKER_COMPOSE} --profile user_management down

um_mm:
	${DOCKER_COMPOSE} exec user_management python manage.py makemigrations

um_migrate:
	${DOCKER_COMPOSE} exec user_management python manage.py migrate

um_shell:
	${DOCKER_COMPOSE} exec user_management python manage.py shell

um_test:
	${DOCKER_COMPOSE} exec user_management python manage.py test


###################### Game #####################
.PHONY: registration_up registration_down

game_up:
	@${DOCKER_COMPOSE} --profile game build
	@${DOCKER_COMPOSE} --profile game up

game_down:
	@${DOCKER_COMPOSE} --profile game down
