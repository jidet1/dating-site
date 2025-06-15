# asgi.py
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import lovematch.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lovematch.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            lovematch.routing.websocket_urlpatterns
        )
    ),
})
