from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes , permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


from ..authenticate import AccessTokenAuthentication
from .utils_oauthtwo import generate_authorization_request_data, get_ft_email, request_ft_token, request_ft_user, login, signup
from .utils import generate_redirect_with_state_cookie
from ..models import OauthTwo, RegistrationUser
from ..common_utils import generate_random_string

import os, requests, time, logging
from .utils_silk import conditional_silk_profile

@api_view(['POST'])
@permission_classes([AllowAny])
def send_authorization_request(request):
    try:
        redirect_uri = os.environ.get('SERVER_URL') + '/callback'
        state = generate_random_string(96)
        hashed_state = generate_authorization_request_data(request, state)
        authorize_url = requests.Request('GET', 'https://api.intra.42.fr/oauth/authorize', params={
            'client_id': os.environ.get('FT_CLIENT_ID'),
            'redirect_uri': redirect_uri,
            'scope': 'public',
            'state': state,
            'response_type': 'code'
        }).prepare().url
        return generate_redirect_with_state_cookie(hashed_state, authorize_url)
    except Exception as e:
        return Response({'oauthtwo_send_authorization_request error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
send_authorization_request = conditional_silk_profile(send_authorization_request, name=send_authorization_request)

#TODO: look into making get_ft_email async to speed up signing up/logging in
@api_view(['POST'])
@permission_classes([AllowAny])
def exchange_code_against_access_token(request):
    try:
        returned_authorization_code = request.data.get("code")
        returned_state = request.data.get("state")
        hashed_state = request.COOKIES.get("state")
        oauthtwo = OauthTwo.objects.get(state=hashed_state)
        if oauthtwo == None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if oauthtwo.check_state(returned_state) == False:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ft_access_token = request_ft_token(returned_authorization_code)
        username = get_ft_email(ft_access_token)
        user = RegistrationUser.objects.filter(username=username).first()
        if oauthtwo.next_step == 'login' or (oauthtwo.next_step == 'signup' and user is not None):
            return login(username)
        if oauthtwo.next_step == 'signup':
            return signup(username)
        raise Exception({'exchange_code_against_access_token: next_step not recognized' : oauthtwo.next_step})
    except Exception as e:
        return Response({'exchange_code_against_access_token': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
exchange_code_against_access_token = conditional_silk_profile(exchange_code_against_access_token, name=exchange_code_against_access_token)
