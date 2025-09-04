from django.shortcuts import render
from django.views.generic import ListView
from .models import Cell

class machineListView(ListView):
    model = Cell
    template_name = 'core/machineList.html'
    context_object_name = 'machines'