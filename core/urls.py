from django.urls import path
from .views import machineListView

urlpatterns = [
    path('', machineListView.as_view(), name='machineList'),
]