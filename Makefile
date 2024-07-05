# Makefile

# Define variables
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip


.PHONY: all install clean-v run run-b stop rm-vol mm migrate shell

all: prep run


prep:
	mkdir -p ~/transcendence_volumes/registration
	mkdir -p ~/transcendence_volumes/user_management
	mkdir -p ~/transcendence_volumes/game
#$(VENV):
#	virtualenv $(VENV)

#install: $(VENV)
#	# Activate virtual environment
#	# Install dependencies
#	. $(VENV)/bin/activate; \
#	$(PIP) install -r srcs/requirements-dev.txt

# Target to clean up
clean-v:
	rm -rf $(VENV)


# Target to run the project

# Activate virtual environment
# Run Django server
run:
	docker compose up

# Other targets as needed
run-b:
	docker compose up --build

run-no-cache:
	docker compose build --no-cache

down:
	docker compose down

rm-vol:
	docker volume rm ft_transcendence_volume_user_management
	docker volume rm ft_transcendence_volume_game

mm:
	docker compose exec web python manage.py makemigrations

migrate:
	docker compose exec web python manage.py migrate

shell:
	docker compose exec web python manage.py shell
