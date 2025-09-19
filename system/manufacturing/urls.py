from django.urls import path
from .views import machineDetails, hrxhr, downtime, defects, addHrxhr

urlpatterns = [
    path('<int:cell_id>/', machineDetails, name='machineDetails'),
    path('<int:cell_id>/hora-por-hora', hrxhr, name='hrxhr'),
    path('<int:cell_id>/hora-por-hora/agregar', addHrxhr, name='addHrxhr'),
    path('<int:cell_id>/tiempo-muerto', downtime, name='downtime'),
    path('<int:cell_id>/defectos', defects, name='defects')
]