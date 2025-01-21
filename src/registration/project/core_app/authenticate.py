from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import RegistrationUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class AccessTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access')
        if not raw_token:
            refresh_token = request.COOKIES.get('refresh')
            if not refresh_token:
                raise AuthenticationFailed('No access token provided')
            else:
                raise AuthenticationFailed('Invalid access token')
        try:
            validated_token = self.get_validated_token(raw_token)
        except AuthenticationFailed:
            raise AuthenticationFailed('Invalid access token')
        return self.get_user(validated_token), validated_token

class RefreshTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('refresh')
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

class CredentialsAuthentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return None
        user = RegistrationUser.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            return None
        return user, None

class BackupCodeAuthentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        backup_code = request.data.get('backup_code')
        if not username or not backup_code or not password:
            return None
        user = RegistrationUser.objects.filter(username=username).first()
        if not user or not user.check_password(password) or not user.check_backup_code(backup_code):
            return None
        return user, None

