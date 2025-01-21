#!/bin/sh

set -e

cd project

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

###

# Creating django admin user
if [ "$DEBUG" = "True" ]; then
    echo "Creating django admin user..."
    cat << EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USERNAME').exists():
    User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')
EOF
    python manage.py runserver 0.0.0.0:8000 &
else
    echo "DEBUG not set or invalid. Running in production mode"
    daphne -b 0.0.0.0 -p 8000 project.asgi:application &
fi
###

exec celery -A project worker --uid 999 --loglevel=info -B
