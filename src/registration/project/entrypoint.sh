#!/bin/sh

python project/manage.py makemigrations
python project/manage.py migrate
exec python project/manage.py runserver 0.0.0.0:8000

