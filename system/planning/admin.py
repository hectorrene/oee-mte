from django.contrib import admin
from .models import plannedDownTime, plannedDownTimeCells, plannedProduction, productionDetail

admin.site.register(plannedDownTime)
admin.site.register(plannedDownTimeCells)
admin.site.register(plannedProduction)
admin.site.register(productionDetail)

