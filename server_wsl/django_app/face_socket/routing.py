from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/recognize_face/?$', consumers.FaceRecognitionConsumer.as_asgi()),
]