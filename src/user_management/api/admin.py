from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser
from .models import MatchRecord


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Additional Info',
            {
                "fields": (
                    'online_status',
                    'friends',
                ),
            },
        ),
    )


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MatchRecord)
