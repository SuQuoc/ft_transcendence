#!/bin/sh

set -e

python project/manage.py makemigrations
python project/manage.py migrate
python project/manage.py collectstatic --noinput

###

# Creating django admin user # TODO: maybe only if DEBUG is True
cat << EOF | python project/manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USERNAME').exists():
    User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')
EOF
###

cd project
python manage.py runserver 0.0.0.0:8000 &
#daphne -b 0.0.0.0 -p 8000 project.asgi:application &

exec celery -A project worker --loglevel=info -B
exec "$@"