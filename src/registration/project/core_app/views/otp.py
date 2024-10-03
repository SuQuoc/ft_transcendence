from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..authenticate import AccessTokenAuthentication, OneTimePasswordAuthentication
from ..models import OneTimePassword
from .utils_otp import send_otp_email, create_one_time_password
from .utils import generate_response_with_valid_JWT


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    try:
        action = request.data.get('action')
        if not action or action not in ['signup', 'login']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        request.user.otp.all().delete()
#            otp.delete()
        password = create_one_time_password(request.user.id, action)
        send_otp_email(request.user.username, action, password) # I need to pass the password to the function because in the future i want to hash it
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'twofa_send_email error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

