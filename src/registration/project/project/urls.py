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

from core_app.views import simple_registration, oauth2
from django.urls import re_path

urlpatterns = [
    re_path('signup', simple_registration.signup),
    re_path('delete_user', simple_registration.delete_user),
    re_path('login', simple_registration.login),
    re_path('logout', simple_registration.logout),
    re_path('change_password', simple_registration.change_password),
    re_path('verify_token', simple_registration.verify_token),
    re_path('refresh_token', simple_registration.refresh_token),
    
    re_path('send_oauth2_authorization_request', oauth2.send_oauth2_authorization_request),
    re_path('exchange_code_against_access_token', oauth2.exchange_code_against_access_token),
    re_path('unset_oauth2', oauth2.unset_oauth2),
    re_path('login_oauth2', oauth2.login_oauth2),
    # [aguilmea] I think i need to modify logout for oauth2 and not writte a own one
]
