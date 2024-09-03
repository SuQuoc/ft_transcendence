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

from core_app.views import oauth2, basic
from django.urls import re_path

urlpatterns = [
    re_path('signup', basic.basic_signup),
    re_path('login', basic.basic_login),

    re_path('delete_user', basic.delete_user),
    re_path('logout', basic.logout),
    re_path('change_password', basic.change_password),
    re_path('verify_token', basic.verify_token),
    re_path('refresh_token', basic.refresh_token),
    re_path('forgot_password', basic.forgot_password),
    re_path('forgot_password_reset', basic.forgot_password_reset),
    
    re_path('send_oauth2_authorization_request', oauth2.send_oauth2_authorization_request),
    re_path('exchange_code_against_access_token', oauth2.exchange_code_against_access_token),
    re_path('unset_oauth2', oauth2.unset_oauth2),
    re_path('login_oauth2', oauth2.login_oauth2),
    # [aguilmea] I think i need to modify logout for oauth2 and not writte a own one
]
