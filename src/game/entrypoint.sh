#!/bin/bash

# cancel if faild
set -e

python manage.py makemigrations pong
python manage.py migrate

echo "Running migrations completed."

# python manage.py collectstatic --noinput
# Creating django admin user
cat << EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJ_SUDO_USERNAME').exists():
    User.objects.create_superuser('$DJ_SUDO_USERNAME', '$DJ_SUDO_EMAIL', '$DJ_SUDO_PASSWORD')
EOF

exec "$@"