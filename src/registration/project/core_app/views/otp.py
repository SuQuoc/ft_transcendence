from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from ..authenticate import AccessTokenAuthentication
from ..models import OneTimePassword
from .utils_otp import send_twofa_email
from ..serializers import OneTimePasswordSerializer

import random
import string

@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def send_email(request):
    try:
        action = request.data.get('action')
        if not action or action not in ['twofa_enable', 'twofa_disable', 'twofa_login']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        otp_data = {
            'related_user': request.user.id,
            'action': action,
            'password': password,
            'expire': timezone.now() + timedelta(minutes=5)
        }
        otp_s = OneTimePasswordSerializer(data=otp_data)
        if not otp_s.is_valid():
            return Response(otp_s.errors, status=status.HTTP_400_BAD_REQUEST)
        otp_s.save()
        send_twofa_email(request.user.username, action, password) # I need to pass the password to the function because in the future i want to hash it
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'twofa_send_email error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# {aguilmea} I think I should send a request to the frontend becuse here i am sending a response to a request they did not send
@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([IsAuthenticated])
def confirm(request):
    try:
        otp = request.data.get('otp')
        action = request.data.get('action')
        if not otp or not action or action not in ['twofa_enable', 'twofa_disable', 'login']:
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
            return Response(status=status.HTTP_200_OK)
        if action == 'twofa_disable':
            request.user.twofa_enabled = False
            return Response(status=status.HTTP_200_OK)
        if action == 'login':
    #       some_login_function(request to get the token_s
    #       return create_response_with_valid_JWT(status.HTTP_200_OK, token_s)
            return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'twofa_confirm error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


