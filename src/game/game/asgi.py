"""
ASGI config for game project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

# Add django channels routing
# https://channels.readthedocs.io/en/latest/tutorial/part_2.html
import django
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from pong.routing import websocket_urlpatterns

from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import UntypedToken, TokenError
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication

from .authenticate import ACCESS
import json


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Extract JWT or other auth token
        print(scope)
        
        cookies = self.get_cookies_from_header(scope['headers'])
        token_str = cookies.get(ACCESS)
        raw_token = token_str.encode('utf-8')
        # NOTE: the encoding back to bytes was only for testing the JWTStatelessUserAuthentication
        # if not used encoding unnecessary
        if not raw_token:
            await send({
                'type': 'websocket.close',
                'code': 4001  # Unauthorized access code, no cookies provided at all, no access cookie provided
            })
            return
        
        from jwt import decode as jwt_decode
        from django.conf import settings
        try:
            data = jwt_decode(raw_token, settings.PUBLIC_KEY, algorithms=["RS256"])
            scope["user_id"] = data["user_id"] # add user_id to the scope
        except Exception as e:
            print("JWT_DECODE")
            print(e)
            await send({
                'type': 'websocket.close',
                'code': 4001  # Unauthorized access code, no cookies provided at all, no access cookie provided
            })
            return
        print(f" uuid: {data}\n")
        
        # NOTE: FOR SOME REASON THIS BLOCK OF CODE DOESN'T WORK, DOES IT WORK IN UM?
        """ auth = JWTStatelessUserAuthentication()
        from django.conf import settings
        print(f"raw_token {raw_token}, public key {settings.PUBLIC_KEY}\n")
        # If token exists, validate it (this part stays the same)
        try:
            #raw_token = auth.get_raw_token(scope['headers'])
            validated_token = auth.get_validated_token(raw_token)
            print(validated_token)
            # Optionally attach user to scope here if needed

        except TokenError:
            # Token invalid, close connection
            await send({
                'type': 'websocket.close',
                'code': 4001  # Unauthorized access code
            })
            return  # Stop further processing
        
        except Exception as e:
            print("EMERGENCY EMERGENCY")
            print(e)
            return """

        # Proceed to the next layer (e.g., the consumer)
        return await super().__call__(scope, receive, send)


    def get_cookies_from_header(self, headers: list):
        cookies = {}
        if isinstance(headers, list):
            for header_name, header_value in headers:
                if header_name == b'cookie':
                    cookie_str = header_value.decode('utf-8') # Decode and parse the cookie header
                    cookies = {k: v for k, v in (item.split('=') for item in cookie_str.split('; '))}
        return cookies
        


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong.settings')
django.setup()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        #"websocket": URLRouter(websocket_urlpatterns)
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(AuthMiddlewareStack( # only used authMiddleware to get the cookies from scope inside the consumer
                URLRouter(websocket_urlpatterns)))
        ),
    }
)



# INSTEAD OF AuthMiddlewareStack, we can use our own custom middleware - COPILOT !!!

# custom_auth_middleware.py which we might need later for JWT auth ??
""" from urllib.parse import parse_qs

class CustomAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        user_id = query_params.get("user_id", [None])[0]
        scope["user_id"] = user_id
        return self.inner(scope)

def CustomAuthMiddlewareStack(inner):
    return CustomAuthMiddleware(AuthMiddlewareStack(inner)) """
