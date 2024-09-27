from django.contrib import admin
from .models import app_planet
from .models import app_cons_period
from .models import app_mm

admin.site.register(app_planet)
admin.site.register(app_cons_period)
admin.site.register(app_mm)