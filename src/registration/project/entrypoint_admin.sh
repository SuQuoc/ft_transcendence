#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

python project/manage.py makemigrations
python project/manage.py migrate
python project/manage.py collectstatic --noinput
###
# Creating django admin user
cat << EOF | python project/manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USERNAME').exists():
    User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')
EOF
###
python project/manage.py runserver 0.0.0.0:8000 &
cd project
exec celery -A project worker --loglevel=info -B
exec "$@"