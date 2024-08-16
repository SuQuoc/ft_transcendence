from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
from jwt.exceptions import InvalidTokenError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if not access_token:
            return None
        try:
            payload = jwt.decode(
                access_token,
                settings.SIMPLE_JWT['VERIFYING_KEY'],
                algorithms=settings.SIMPLE_JWT['ALGORITHM'],
                audience=None,  # If your token expects an audience, set it here
                options={"verify_exp": True},
            )
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Invalid token: No user_id')

            # Fetch the user from the database
            User = get_user_model()
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed('No user found for this token')

            # Return the authenticated user and None for the auth
            return (user, None)
        except InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
