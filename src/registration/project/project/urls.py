"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from core_app.views import common, oauth2, basic, otp
from django.urls import re_path

urlpatterns = [
    # basic views
    re_path('signup', basic.signup),
    re_path('login', basic.login),
    re_path('forgot_password_send_email', basic.forgot_password_send_email),
    re_path('forgot_password_reset', basic.forgot_password_reset),

    # common views
    re_path('delete_user', common.delete_user),
    re_path('logout', common.logout),
    re_path('change_password', common.change_password),
    re_path('verify_token', common.verify_token),
    re_path('refresh_token', common.refresh_token),
    
    # oauth2 views
    re_path('oauth2_callback', oauth2.callback),
    re_path('oauth2_set', oauth2.set),
    re_path('oauth2_unset', oauth2.unset),
    re_path('oauth2_signup', oauth2.signup),
    re_path('oauth2_login', oauth2.login),

    # twofa views
    re_path('otp_send_email', otp.send_email),
    re_path('otp_confirm', otp.confirm),


]
