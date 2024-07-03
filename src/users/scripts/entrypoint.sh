#!/bin/bash

python manage.py migrate

cat << EOF | python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJ_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJ_SUPERUSER_USERNAME', '$DJ_SUPERUSER_EMAIL', '$DJ_SUPERUSER_PASSWORD')
EOF

python manage.py runserver 0.0.0.0:8000