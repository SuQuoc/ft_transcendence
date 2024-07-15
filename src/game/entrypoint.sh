#!/bin/bash

# cancel if faild
set -e

python manage.py makemigrations pong
python manage.py migrate

echo "Running migrations completed."

exec "$@"