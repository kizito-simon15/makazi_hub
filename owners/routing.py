from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from owners.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    "websocket": URLRouter(
        websocket_urlpatterns
    ),
})
