from rest_framework_simplejwt.tokens import RefreshToken

def generate_token(user_id):
    refresh = RefreshToken()
    refresh["user_id"] = str(user_id)
    access_token = str(refresh.access_token)
    return access_token


# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
# from rest_framework.exceptions import AuthenticationFailed
# from api.models import CustomUser

# old
# class CustomJWTAuthentication(JWTAuthentication):
#     def get_user(self, validated_token):
#         try:
#             user_id = validated_token['user_id']
#         except KeyError:
#             raise InvalidToken("Token contained no recognizable user identification")
#         return user_id
#
#     def authenticate(self, request):
#         header = self.get_header(request)
#         if header is None:
#             return None
#
#         raw_token = self.get_raw_token(header)
#         if raw_token is None:
#             return None
#
#         validated_token = self.get_validated_token(raw_token)
#         user_id = self.get_user(validated_token)
#
#         return (user_id, validated_token) # DRF sets return values to request.user and request.auth
