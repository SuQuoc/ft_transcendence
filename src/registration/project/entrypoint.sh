#!/bin/sh

set -e

python project/manage.py makemigrations
python project/manage.py migrate
python project/manage.py collectstatic --noinput
python project/manage.py runserver 0.0.0.0:8000 &
cd project
exec celery -A project worker --loglevel=info -B
exec "$@"