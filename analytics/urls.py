from django.urls import path
from .views import machineListView, machineDashboard

urlpatterns = [
    path('', machineListView.as_view(), name='analyticsList'),
    path('<int:cell_id>/', machineDashboard, name='machineDashboard')
]