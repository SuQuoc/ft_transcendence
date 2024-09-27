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

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def confirm_twofa(request):
    try:
        otp = request.data.get('otp')
        action = request.data.get('action')
        if not otp or not action or action not in ['twofa_enable', 'twofa_disable']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        stored_otp = OneTimePassword.objects.filter(related_user=request.user.id).first()
        if not stored_otp:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if stored_otp.expire < timezone.now():
            return Response({str(stored_otp.expire) : str(timezone.now())}, status=status.HTTP_401_UNAUTHORIZED)
        if stored_otp.action != action:
            return Response({stored_otp.action : action}, status=status.HTTP_401_UNAUTHORIZED)
        if stored_otp.password != otp:
            return Response({stored_otp.password : otp}, status=status.HTTP_401_UNAUTHORIZED)
        if action == 'twofa_enable':
            request.user.twofa_enabled = True
            request.user.save()
            return Response(status=status.HTTP_200_OK)
        if action == 'twofa_disable':
            request.user.twofa_enabled = False
            request.user.save()
            return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'twofa_confirm error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([OneTimePasswordAuthentication])
@permission_classes([IsAuthenticated])
def confirm_login(request):
    try:
        token_s = TokenObtainPairSerializer(data=request.data)
        return generate_response_with_valid_JWT(status.HTTP_200_OK, token_s)
    except Exception as e:
        return Response({'twofa_confirm error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


