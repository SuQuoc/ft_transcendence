from django.contrib.auth import get_user_model
from django.conf import settings
import jwt
from jwt.exceptions import InvalidTokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from api.models import CustomUser




class CookieJWTAuthentication(JWTTokenUserAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if not access_token:
            return None
        validated_token = self.get_validated_token(access_token)
        # enforce_csrf(request)
        # raise AuthenticationFailed('CreateUserAuth')
        return self.get_user(validated_token), validated_token 
        

