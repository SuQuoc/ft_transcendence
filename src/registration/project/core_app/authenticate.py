from rest_framework_simplejwt.authentication import JWTAuthentication

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
        
class NoTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):    
        return (None, None)

