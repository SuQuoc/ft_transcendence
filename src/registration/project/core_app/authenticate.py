from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
from jwt.exceptions import InvalidTokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class AccessTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_cookie = request.COOKIES.get('access')
        if not access_cookie:
            return None
        try:
            payload = jwt.decode(
                access_cookie,
                settings.SIMPLE_JWT['VERIFYING_KEY'],
                algorithms=settings.SIMPLE_JWT['ALGORITHM'],
                options={"verify_exp": True},
            )
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Invalid token: No user_id')
            User = get_user_model()
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed('No user found for this token')
            return (user, None)
        except InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        
class RefreshTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):

        refresh_cookie = request.COOKIES.get('refresh')
        if not refresh_cookie:
            return None
        try:
            payload = jwt.decode(
                refresh_cookie,
                settings.SIMPLE_JWT['VERIFYING_KEY'],
                algorithms=settings.SIMPLE_JWT['ALGORITHM'],
                options={"verify_exp": True},
            )
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Invalid token: No user_id')
            User = get_user_model()
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed('No user found for this token')
            return (user, None)
        except InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
