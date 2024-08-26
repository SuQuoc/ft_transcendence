DOCKER_COMPOSE = docker compose -f ./docker_compose_files/docker-compose.yml



###################### General #####################
.PHONY: all up build_up build_no_cache down build_only rm_vol clean fclean re new keys

all: up

up:
	${DOCKER_COMPOSE} --profile all up

build_up:
	${DOCKER_COMPOSE} --profile all up --build

build_no_cache:
	${DOCKER_COMPOSE} --profile all build --no-cache

down:
	${DOCKER_COMPOSE} --profile all down

build_only:
	${DOCKER_COMPOSE} --profile all build

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
.PHONY: reg_cache_clean

reg_cache_clean:
	rm -rf ./src/registration/project/core_app/__pycache__/
	rm -rf ./src/registration/project/core_app/migrations/__pycache__/
	rm -rf ./src/registration/project/core_app/migrations/0001_initial.py
	rm -rf ./src/registration/project/core_app/views/__pycache__/
	rm -rf ./src/registration/project/project/__pycache__/


###################### Game #####################
.PHONY: game_cache_clean

game_cache_clean:
	rm -rf ./src/game/__pycache__/
	rm -rf ./src/pong/__pycache__/
	rm -rf ./src/pong/game_core/__pycache__/
	rm -rf ./src/pong/migrations/__pycache__/
	rm -rf ./src/pong/migrations/0001_initial.py

###################### User Management #####################
.PHONY: um_up um_down um_mm um_migrate um_shell um_cache_clean

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

um_exec:
	${DOCKER_COMPOSE} exec user_management bash

um_db_exec:
	${DOCKER_COMPOSE} exec db_user_management bash

um_test:
	${DOCKER_COMPOSE} exec user_management python manage.py test

um_cache_clean:
	rm -rf ./src/user_management/__pycache__/
	rm -rf ./src/user_management/api/__pycache__/
	rm -rf ./src/user_management/api/management/__pycache__/
	rm -rf ./src/user_management/api/management/commands/__pycache__/
	rm -rf ./src/user_management/api/migrations/__pycache__/
	rm -rf ./src/user_management/api/migrations/0001_initial.py
	rm -rf ./src/user_management/api/migrations/0002_customuser_image.py
	rm -rf ./src/user_management/friends/migrations/__pycache__/
	rm -rf ./src/user_management/friends/__pycache__/
	rm -rf ./src/user_management/friends/migrations/0001_initial.py
	rm -rf ./src/user_management/friends/tests/__pycache__/
	rm -rf ./src/user_management/user_management/__pycache__/

###################### Game #####################
.PHONY: registration_up registration_down

game_up:
	@${DOCKER_COMPOSE} --profile game build
	@${DOCKER_COMPOSE} --profile game up

game_down:
	@${DOCKER_COMPOSE} --profile game down

test: down
	@make re > /dev/null 2>&1 &
	@PID=$$!
	@wait $$PID
	@while ! nc -z localhost 8000; do \
		echo "* Waiting for the server to start..."; \
		sleep 2; \
	done
	pytest ./tests/playwright_tests/test_basic.py
	@make down
