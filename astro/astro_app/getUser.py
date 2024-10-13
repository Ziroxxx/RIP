from .models import AuthUser
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import redis

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def getUserBySession(request):
    ssid = request.COOKIES.get('session_id')
    if ssid:
        try:
            username = session_storage.get(ssid).decode('utf-8')
            user = AuthUser.objects.get(username=username)
        except AttributeError:
            user = AnonymousUser()
    else:
        user = AnonymousUser() 
    return user