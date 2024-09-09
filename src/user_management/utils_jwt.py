from rest_framework_simplejwt.tokens import RefreshToken
from api.models import CustomUser
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed



def generate_token(user_id):
    refresh = RefreshToken()
    refresh["user_id"] = str(user_id)
    access_token = str(refresh.access_token)
    return access_token


def get_user_from_jwt(request):
    try:
        user = CustomUser.objects.get(user_id=request.user.user_id)
    except CustomUser.DoesNotExist:
        raise AuthenticationFailed("Invalid user ID in JWT (either our mistake or u sus)")
    return user