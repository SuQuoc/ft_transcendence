from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import RegistrationUser, OneTimePassword
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication

class AccessTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access')
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

class RefreshTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('refresh')
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
          
class OneTimePasswordAuthentication(BaseAuthentication):
    def authenticate(self, request, password=None):
        otp = request.data.get('otp')
        username = request.data.get('username')
        if not otp or not username:
            return None
        user = RegistrationUser.objects.filter(username=username).first()
        stored_otp = OneTimePassword.objects.filter(related_user=user.id).first()
        if not stored_otp:
            return None
        if stored_otp.expire < timezone.now():
            return None
        if stored_otp.password != otp:
            return None
        return user, None


class UsernameAuthentication(BaseAuthentication):
    def authenticate(self, request, password=None):
        username = request.data.get('username')
        if not username:
            return None
        user = RegistrationUser.objects.filter(username=username).first()
        return user, None
    
