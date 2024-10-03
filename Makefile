DOCKER_COMPOSE = docker compose -f ./docker_compose_files/docker-compose.yml



###################### General #####################
.PHONY: all up build_up build_no_cache down build_only rm_vol rm_keys clean fclean re new keys cache_clean

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

rm_keys:
	rm -rf ./src/common_files/jwt__keys
	rm -rf ./src/common_files/ssl_certs

clean: down
	docker system prune -f

fclean: down rm_vol rm_keys
	docker system prune -af

re: down rm_vol cache_clean build_up

new: fclean build_up

keys:
	bash ./src/common_files/jwt_create_keys.sh
	bash ./src/common_files/ssl_create_keys.sh

cache_clean:	game_cache_clean reg_cache_clean um_cache_clean


###################### Registration #####################
.PHONY: reg_cache_clean

reg_cache_clean:
	rm -rf ./src/registration/project/core_app/__pycache__/
	rm -rf ./src/registration/project/core_app/migrations/__pycache__/
	find ./src/registration/project/core_app/migrations/ -type f ! -name '__init__.py' -delete
	rm -rf ./src/registration/project/core_app/views/__pycache__/
	rm -rf ./src/registration/project/project/__pycache__/


###################### Game #####################
.PHONY: game_cache_clean

game_cache_clean:
	rm -rf ./src/game/__pycache__/
	rm -rf ./src/game/game/__pycache__/
	rm -rf ./src/game/pong/__pycache__/
	rm -rf ./src/game/pong/game_code/__pycache__/
	rm -rf ./src/game/pong/migrations/__pycache__/
	find ./src/game/pong/migrations/ -type f ! -name '__init__.py' -delete

###################### User Management #####################
.PHONY: um_up um_down um_mm um_migrate um_shell um_cache_clean

um_up:
	@${DOCKER_COMPOSE} --profile user_management build
	@${DOCKER_COMPOSE} --profile user_management up

um_down:
	@${DOCKER_COMPOSE} --profile user_management down

um_mm:
	${DOCKER_COMPOSE} exec usermanagement python manage.py makemigrations


um_migrate:
	${DOCKER_COMPOSE} exec usermanagement python manage.py migrate

um_shell:
	${DOCKER_COMPOSE} exec usermanagement python manage.py shell

um_exec:
	${DOCKER_COMPOSE} exec usermanagement bash

um_db_exec:
	${DOCKER_COMPOSE} exec db_user_management bash

um_test:
	${DOCKER_COMPOSE} exec usermanagement python manage.py test

um_cache_clean:
	rm -rf ./src/user_management/__pycache__/
	rm -rf ./src/user_management/api/__pycache__/
	rm -rf ./src/user_management/api/management/__pycache__/
	rm -rf ./src/user_management/api/management/commands/__pycache__/
	rm -rf ./src/user_management/api/migrations/__pycache__/
	find ./src/user_management/api/migrations/ -type f ! -name '__init__.py' -delete
	rm -rf ./src/user_management/friends/migrations/__pycache__/
	rm -rf ./src/user_management/friends/__pycache__/
	find ./src/user_management/friends/migrations/ -type f ! -name '__init__.py' -delete
	rm -rf ./src/user_management/friends/tests/__pycache__/
	rm -rf ./src/user_management/user_management/__pycache__/

###################### Game #####################
.PHONY: registration_up registration_down test test_running

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
	pytest ./tests/playwright_tests
	@make down

test_running:
	pytest ./tests/playwright_tests
