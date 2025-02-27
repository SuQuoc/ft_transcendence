DOCKER_COMPOSE = docker compose -f ./docker_compose_files/docker-compose.yml



###################### General #####################
.PHONY: all up build_up build_no_cache down build_only rm_vol rm_keys clean fclean re new keys cache_clean

all: up

up: keys
	${DOCKER_COMPOSE} up

build_up:
	${DOCKER_COMPOSE} up --build

build_no_cache:
	${DOCKER_COMPOSE} build --no-cache

down:
	${DOCKER_COMPOSE} down

build_only:
	${DOCKER_COMPOSE} build

rm_vol:
	docker volume prune -af

rm_keys:
	rm -rf ./src/common_files/jwt__keys
	rm -rf ./src/common_files/ssl_certs

clean: down
	docker system prune -f

fclean: down rm_vol rm_keys cache_clean
	docker system prune -af

re: down rm_vol cache_clean build_up

new: fclean keys build_up

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
	rm -rf ./src/registration/*.prof
	rm -rf ./src/registration/project/staticfiles
	rm -rf ./src/registration/project/emails

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


test: down
	@make re > /dev/null 2>&1 &
	@PID=$$!
	@wait $$PID
	@while ! nc -z localhost 8443; do \
		echo "* Waiting for the server to start..."; \
		sleep 2; \
	done
	pytest ./tests/playwright_tests
	@make down

test_tournament: down
	@make re > /dev/null 2>&1 &
	@PID=$$!
	@wait $$PID
	@while ! nc -z localhost 8443; do \
		echo "* Waiting for the server to start..."; \
		sleep 2; \
	done
	pytest ./tests/playwright_tests/test_tournament_multiple.py
	@make down

test_running:
	pytest ./tests/playwright_tests/
# pytest ./tests/playwright_tests/test_tournament_multiple.py::TestTournamentMultiple::test_tournament_bracket
