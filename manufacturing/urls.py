from django.urls import path
from .views import machineDetails, addProduction, downtime, defects, addHrxhr, hrxhr, recap

urlpatterns = [
    path('<int:cell_id>/', machineDetails, name='machineDetails'),
    path('<int:cell_id>/hora-por-hora/agregar', addHrxhr, name='addHrxhr'),
    path('<int:cell_id>/hora-por-hora/registrar', hrxhr, name='registerHrxhr'),
    path('<int:cell_id>/hora-por-hora', addProduction, name='hrxhr'),
    path('<int:cell_id>/tiempo-muerto', downtime, name='downtime'),
    path('<int:cell_id>/defectos', defects, name='defects'),
    path('<int:cell_id>/cerrar-dia', recap, name='recap'),
]