from django.contrib import admin

from .models import CustomUser

# Register your models here.


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'displayname', 'image', 'created_at', 'updated_at']
    search_fields = ('displayname',)


admin.site.register(CustomUser, CustomUserAdmin)
