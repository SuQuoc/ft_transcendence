#!/bin/bash

# cancel if faild
set -e

python manage.py makemigrations api
python manage.py migrate

cat << EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJ_SUDO_USERNAME_MANAGEMENT').exists():
    User.objects.create_superuser('$DJ_SUDO_USERNAME_MANAGEMENT', '$DJ_SUDO_EMAIL_MANAGEMENT', '$DJ_SUDO_PASSWORD_MANAGEMENT')
EOF

exec "$@"
