from django.urls import path
from .views import productionPlan, machineListView, addProduction, downTimeListView, plannedDownTime, addDownTime

urlpatterns = [
    path('produccion-maquinas', machineListView.as_view(), name='planningMachineList'),
    path('tiempo-muerto-maquinas', downTimeListView.as_view(), name='downTimeList'),
    path('<int:cell_id>/produccion/', productionPlan, name='productionPlan'),
    path('<int:cell_id>/tiempo-muerto/', plannedDownTime, name='downTimePlan'),
    path('anadir-produccion/', addProduction, name='addProduction'),
    path('anadir-tiempo-muerto/', addDownTime, name = 'addDownTime')
]
