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

from core_app.views import common, oauthtwo, basic, otp, test
from django.urls import path

urlpatterns = [
    
    # basic views
    path('registration/basic_login', basic.login),
    path('registration/basic_forgot_password', basic.forgot_password),
    path('registration/basic_signup', basic.signup),
    path('registration/basic_signup_change_password', basic.signup_change_password),
    path('registration/basic_signup_change_username', basic.signup_change_username),
   
    # oauth2 views
    path('registration/oauthtwo_send_authorization_request', oauthtwo.send_authorization_request),
    path('registration/oauthtwo_exchange_code_against_access_token', oauthtwo.exchange_code_against_access_token),
    path('registration/oauthtwo_signup', oauthtwo.signup),
    path('registration/oauthtwo_login', oauthtwo.login),
    #path('registration/oauthtwo_callback', oauthtwo.callback),
    path('registration/oauthtwo_set', oauthtwo.set),
    path('registration/oauthtwo_unset', oauthtwo.unset),


    # twofa views
    path('registration/otp_send_otp', otp.send_otp),

    # common views
    path('registration/change_password', common.change_password),
    path('registration/change_username', common.change_username),
    path('registration/delete_user', common.delete_user),
    path('registration/logout', common.logout),
    path('registration/refresh_token', common.refresh_token),
    path('registration/verify_token', common.verify_token),

    #test views # [aguilmea] to be deleted as soon as frontend changed the endpoint
    path('registration/signup', test.signup), # [aguilmea] to be deleted as soon as frontend changed the endpoint
    path('registration/login', test.login), # [aguilmea] to be deleted as soon as frontend changed the endpoint
]
