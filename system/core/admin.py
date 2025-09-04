from django.contrib import admin
from .models import Model, Cell, Cause, modelRouting

admin.site.register(Model)
admin.site.register(Cell)
admin.site.register(Cause)
admin.site.register(modelRouting)