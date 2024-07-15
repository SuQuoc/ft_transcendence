# Makefile

# Variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Volume
VOL_DIR = ~/transcendence_volumes
VOL_PREFIX = ft_transcendence_volume_

# Services
S_REGI = registration
S_USER = user_management
S_GAME = game


.PHONY: all prep install clean-v up up-b stop rm-vol mm migrate shell


all: prep up


prep:
	mkdir -p $(VOL_DIR)/$(S_REGI)
	mkdir -p $(VOL_DIR)/$(S_USER)
	mkdir -p $(VOL_DIR)/$(S_GAME)
#$(VENV):
#	virtualenv $(VENV)

#install: $(VENV)
#	# Activate virtual environment
#	# Install dependencies
#	. $(VENV)/bin/activate; \
#	$(PIP) install -r srcs/user_management/requirements.txt

# Target to clean up
clean-v:
	rm -rf $(VENV)

up: prep
	docker compose --profile all up

up-b: prep
	docker compose --profile all up --build

build-no-cache:
	docker compose --profile all build --no-cache

down:
	docker compose --profile all down

rm-vol:
	docker volume rm $(VOL_PREFIX)$(S_USER)
	docker volume rm $(VOL_PREFIX)$(S_GAME)
	rm -rf $(VOL_DIR)

# Commands for user_management service
mm:
	docker compose exec $(S_USER) python manage.py makemigrations

migrate:
	docker compose exec $(S_USER) python manage.py migrate

shell:
	docker compose exec $(S_USER) python manage.py shell


###################### Annie #####################

registration_up:
	@mkdir -p $(VOL_DIR)/$(S_REGI)
	@docker compose -f ./registration.yml --profile registration build
	@docker compose -f ./registration.yml --profile registration up

registration_down:
	@docker compose -f ./registration.yml --profile registration down
	@rm -rf $(VOL_DIR)/$(S_REGI)


###################### Quocsu #####################

user_management_up:
	@mkdir -p $(VOL_DIR)/$(S_USER)
	@docker compose -f ./user_management.yml --profile user_management build
	@docker compose -f ./user_management.yml --profile user_management up

user_management_down:
	@docker compose -f ./user_management.yml --profile user_management down
	@rm -rf $(VOL_DIR)/$(S_USER)
