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

from core_app.views import common, oauth2, basic, otp, test
from django.urls import path

urlpatterns = [
    # basic views
    path('registration/basic_signup/', basic.signup),
    path('registration/basic_login/', basic.login),
    path('registration/forgot_password/', basic.forgot_password_send_email),

    #test views
    path('registration/signup/', test.signup),
    path('registration/login/', test.login),

    # common views
    path('registration/delete_user/', common.delete_user),
    path('registration/logout/', common.logout),
    path('registration/change_password/', common.change_password),
    path('registration/verify_token/', common.verify_token),
    path('registration/refresh_token/', common.refresh_token),
    
    # oauth2 views
    path('registration/oauth2_callback/', oauth2.callback),
    path('registration/oauth2_set/', oauth2.set),
    path('registration/oauth2_unset/', oauth2.unset),
    path('registration/oauth2_signup/', oauth2.signup),
    path('registration/oauth2_login/', oauth2.login),

    # twofa views
    path('registration/otp_send_email/', otp.send_email),
    path('registration/otp_confirm_twofa/', otp.confirm_twofa),
    path('registration/otp_confirm_login/', otp.confirm_login),


]
