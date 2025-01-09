"""
ASGI config for user_management project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management.settings')
django.setup()
django_asgi_app = get_asgi_application()


from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from friends.routing import websocket_urlpatterns

from channels.middleware import BaseMiddleware
from .authenticate import ACCESS

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
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
            print(e)
            await send({
                'type': 'websocket.close',
                'code': 4001  # Unauthorized access code, no cookies provided at all, no access cookie provided
            })
            return
        return await super().__call__(scope, receive, send)


    def get_cookies_from_header(self, headers: list):
        cookies = {}
        if isinstance(headers, list):
            for header_name, header_value in headers:
                if header_name == b'cookie':
                    cookie_str = header_value.decode('utf-8') # Decode and parse the cookie header
                    cookies = {k: v for k, v in (item.split('=') for item in cookie_str.split('; '))}
        return cookies


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(
                AuthMiddlewareStack(
                    URLRouter(
                        websocket_urlpatterns
                    )
                )
            )
        ),
    }
)
