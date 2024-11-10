from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication


ACCESS = "access"

# raw_token = access token
class CookieJWTAuthentication(JWTStatelessUserAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get(ACCESS)
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        request.validated_token = validated_token
		# enforce_csrf(request)
        # raise AuthenticationFailed('CreateUserAuth')
        return self.get_user(validated_token), validated_token
    
	