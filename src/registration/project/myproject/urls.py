"""
URL configuration for myproject project.

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
#from django.contrib import admin # [aguilmea] deleted manually for now
#from django.urls import path # [aguilmea] deleted manually
from django.urls import re_path # [aguilmea] added manually
from . import views # [aguilmea] added manually

urlpatterns = [
#    path('admin/', admin.site.urls), # [aguilmea] deleted manuallyfor now
    re_path('login', views.login), # [aguilmea] added 
    re_path('signup', views.signup), # [aguilmea] added 
    re_path('test_token', views.test_token), # [aguilmea] added 
]