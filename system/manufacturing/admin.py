from django.contrib import admin
from .models import Defect, DownTime, Production

admin.site.register(Defect)
admin.site.register(DownTime)
admin.site.register(Production)
