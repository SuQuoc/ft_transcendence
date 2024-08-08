"""
URL configuration for user_management project.

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

from api import views
from api.views import MyTokenObtainPairView  # register service
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = (
    [
        path("um/admin/", admin.site.urls),
        # path("um/profile/", views.profile, name="profile"), # delete later, just for testing if server is still rendering changes
        path('um/api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # register service
        path('um/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # register service
        path("um/api/friend-request/", include("friends.urls")),
        path("um/api/", include("api.urls")),
    ]

)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
