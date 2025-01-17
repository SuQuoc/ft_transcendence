#!/bin/sh

set -e

python project/manage.py makemigrations
python project/manage.py migrate
python project/manage.py collectstatic --noinput

###

# Creating django admin user
if [ "$DEBUG" = "True" ]; then
    echo "Creating django admin user..."
    cat << EOF | python project/manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJ_SUDO_USERNAME').exists():
    User.objects.create_superuser('$DJ_SUDO_USERNAME', '$DJ_SUDO_EMAIL', '$DJ_SUDO_PASSWORD')
EOF
fi
###

cd project
python manage.py runserver 0.0.0.0:8000 &
#daphne -b 0.0.0.0 -p 8000 project.asgi:application &


exec celery -A project worker --uid 999 --loglevel=info -B
exec "$@"