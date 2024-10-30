from django.contrib import admin
from .models import RegistrationUser, OneTimePassword, OauthTwo

# Register your models here.

class RegistrationUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'setup_date', 'last_login', 'email_verified']
    search_fields = ('username',)

class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ['related_user', 'password', 'action', 'expire']
    search_fields = ('related_user__username',)

class OauthTwoAdmin(admin.ModelAdmin):
    list_display = ['id', 'next_step', 'related_user']
    search_fields = ('related_user__username',)

admin.site.register(RegistrationUser, RegistrationUserAdmin)
admin.site.register(OneTimePassword, OneTimePasswordAdmin)
admin.site.register(OauthTwo, OauthTwoAdmin)
