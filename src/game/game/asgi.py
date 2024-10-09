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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong.settings')
django.setup()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        #"websocket": URLRouter(websocket_urlpatterns)
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
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
