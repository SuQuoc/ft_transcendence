#!/bin/bash

# cancel if faild
set -e

python manage.py makemigrations
python manage.py migrate

#TODO: uncomment when checking for deployment
#python manage.py collectstatic --noinput

# Creating django admin user
cat << EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJ_SUDO_USERNAME').exists():
    User.objects.create_superuser('$DJ_SUDO_USERNAME', '$DJ_SUDO_EMAIL', '$DJ_SUDO_PASSWORD')
EOF

# Run custom command
python manage.py create_testusers # TODO: delete this line when deploying

exec "$@"
