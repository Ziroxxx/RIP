from django.contrib import admin
from .models import planets
from .models import requests
from .models import mm

admin.site.register(planets)
admin.site.register(requests)
admin.site.register(mm)