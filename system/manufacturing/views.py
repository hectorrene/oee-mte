from django.shortcuts import render, get_object_or_404
from planning.models import plannedDownTime, plannedDownTimeCells, plannedProduction, productionDetail
from .models import Defect
from core.models import Cell, modelRouting 
from django.db.models import Q
from django.utils import timezone

def machineDetails(request, cell_id):
    cell = get_object_or_404(Cell, id=cell_id)
    today = timezone.localdate()
    downtimes = plannedDownTime.objects.filter(downtime__cell=cell, is_active=True).filter( 
        Q(valid_from__lte=today, valid_to__gte=today)
    )
    plannings = plannedProduction.objects.filter(cell=cell)
    production_details = productionDetail.objects.filter(planned_production__cell=cell)
    planned_today = plannedProduction.objects.filter(cell=cell, date=today)

    production_summary = []
    total_pieces = 0

    context = {
        'cell': cell,
        'downtimes': downtimes,
        'plannings': plannings,
        'production_details': production_details,
        'planned_today': planned_today,
        'today': today,
    }

    return render(request, 'manufacturing/machineDetails.html', context)

def hrxhr (request, cell_id):
    cell = get_object_or_404(Cell, id=cell_id)
    today = timezone.localdate()
    production_details = productionDetail.objects.filter(planned_production__cell=cell)
    planned_today = plannedProduction.objects.filter(cell=cell, date=today)

    context = {
        'cell': cell,
        'planned_today': planned_today,
        'today': today,
    }

    return render(request, 'manufacturing/hrxhr.html', context)

def downtime (request, cell_id):
    cell = get_object_or_404(Cell, id=cell_id)
    today = timezone.localdate()

    context = {
        'cell': cell, 
        'today': today,
    }

    return render(request, 'manufacturing/downtime.html', context)

def defects (request, cell_id): 
    cell = get_object_or_404(Cell, id=cell_id)
    today = timezone.localdate()

    context = {
        'cell': cell, 
        'today': today,
    }

    return render(request, 'manufacturing/defects.html', context)


