from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes , permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import redirect

from ..authenticate import AccessTokenAuthentication
from .utils_oauthtwo import generate_authorization_request_data, get_ft_email, request_ft_token, request_ft_user, login, signup
from ..models import OauthTwo, RegistrationUser
from .utils_oauthtwo import check_password

import requests
import os


@api_view(['POST'])
@authentication_classes([AccessTokenAuthentication])
@permission_classes([AllowAny])
def send_authorization_request(request):
    try:
        redirect_uri = os.environ.get('SERVER_URL') + '/callback'
        state = generate_authorization_request_data(request)
        authorize_url = requests.Request('GET', 'https://api.intra.42.fr/oauth/authorize', params={
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'redirect_uri': redirect_uri,
            'scope': 'public',
            'state': state,
            'response_type': 'code'
        }).prepare().url
        redirect(authorize_url) # Redirect the user to the authorization URL
        # [aguilmea] i want to set a cookie with the state
        return Response({authorize_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'oauthtwo_send_authorization_request error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def exchange_code_against_access_token(request):
    try:
        returned_authorization_code = request.data.get("code")
        returned_state = request.data.get("state")
        #hashed_state = request.COOKIES.get("state")
        # if check_password(returned_state, set_state) == False:
        #    return Response(status=status.HTTP_401_UNAUTHORIZED
        #oauthtwo = OauthTwo.objects.get(state=hashed_state)
        oauthtwo = OauthTwo.objects.get.first() # [aguilmea] temporary until the cookie is set in send_authorization_request
        if oauthtwo == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ft_access_token = request_ft_token(returned_authorization_code)
        username = get_ft_email(ft_access_token)
        user = RegistrationUser.objects.filter(username=username).first()
        if oauthtwo.next_step == 'login' or (oauthtwo.next_step == 'signup' and user is not None):
            return login(ft_access_token)
        if oauthtwo.next_step == 'signup':
            return signup(ft_access_token)
        raise Exception({'exchange_code_against_access_token: next_step not recognized' : oauthtwo.next_step})
    except Exception as e:
        return Response({'exchange_code_against_access_token': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
