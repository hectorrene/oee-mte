from django.shortcuts import render
from django.views.generic import ListView, DetailView
from core.models import Cell

class machineListView(ListView):
    model = Cell
    template_name = 'analytics/analyticsList.html'
    context_object_name = 'machines'
