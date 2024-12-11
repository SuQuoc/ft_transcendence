from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.utils import timezone
from datetime import timedelta

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task
def non_verified_users_after_one_day():
    from core_app.models import RegistrationUser
    one_day_ago = timezone.now() - timedelta(days=1)
    #one_day_ago = timezone.now() - timedelta(minutes=1) # for testing purpose
    users_to_delete = RegistrationUser.objects.filter(

        email_verified=False,
        date_joined__lt=one_day_ago
    ).exclude(username=os.environ.get("ADMIN_USERNAME"))
    nb = users_to_delete.count()
    users_to_delete.delete()
    return nb

@app.task
def users_without_login_within_one_year():
    from core_app.models import RegistrationUser
    one_year_ago = timezone.now() - timedelta(days=365)
    #one_year_ago = timezone.now() - timedelta(minutes=2) # for testing purpose
    users_to_delete = RegistrationUser.objects.filter(last_login__lt=one_year_ago).exclude(username=os.environ.get("ADMIN_USERNAME"))
    nb = users_to_delete.count()
    users_to_delete.delete()
    return nb