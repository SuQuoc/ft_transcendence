#!/bin/bash

# cancel if faild
set -e

python manage.py makemigrations
python manage.py migrate

if [ "$TEST" = "True" ]; then 
    echo "Creating test users..."
    python manage.py create_testusers # Run custom command
fi


if [ "$DEBUG" = "True" ]; then
    echo "Creating django admin user..."
    cat << EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJ_SUDO_USERNAME').exists():
    User.objects.create_superuser('$DJ_SUDO_USERNAME', '$DJ_SUDO_EMAIL', '$DJ_SUDO_PASSWORD')
EOF
    python manage.py runserver 0.0.0.0:8000 
else
    echo "DEBUG not set or invalid. Running in production mode"
    daphne -b 0.0.0.0 -p 8000 user_management.asgi:application
fi

