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

from core_app import views
from django.contrib import admin
from django.urls import re_path

urlpatterns = [
    re_path('signup', views.signup),
    re_path('delete_user', views.delete_user),
    re_path('login', views.login),
    re_path('logout', views.logout),
    re_path('change_password', views.change_password),
    re_path('verify_token', views.verify_token),
    re_path('refresh_token', views.refresh_token),
]
