from django.contrib import admin
from .models import Defect, DownTime, Production, hourlyProduction

admin.site.register(Defect)
admin.site.register(DownTime)
admin.site.register(Production)
admin.site.register(hourlyProduction)