from django.shortcuts import render, get_object_or_404, redirect
from .models import plannedDownTime, plannedDownTimeCells, plannedProduction, productionDetail
from core.models import Cell, Model
from django.views.generic import ListView, CreateView
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import PlannedProductionForm, ProductionDetailFormSet, plannedDownTimeForm

class machineListView(ListView):
    model = Cell
    template_name = 'planning/machineList.html'
    context_object_name = 'machines'

def productionPlan(request, cell_id):
    cell = get_object_or_404(Cell, id=cell_id)
    week_offset = int(request.GET.get('week_offset', 0))
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    target_monday = monday + timedelta(weeks=week_offset)
    workdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

    week_dates = []
    for i in range(5):  # 5 días laborales
        week_dates.append(target_monday + timedelta(days=i))
    
    # Obtener la producción planeada para esta celda y semana
    production_data = plannedProduction.objects.filter(
        cell=cell,
        date__range=[week_dates[0], week_dates[-1]]
    ).prefetch_related('details__model_routing')
    
    # Organizar los datos por fecha
    production_by_date = {}
    for production in production_data:
        production_by_date[production.date] = production.details.all()
    
    # Preparar el contexto para el template
    calendar_data = []
    for date in week_dates:
        day_data = {
            'date': date,
            'day_name': date.strftime('%A'),
            'day_short': date.strftime('%a'),
            'day_number': date.day,
            'details': production_by_date.get(date, [])
        }
        calendar_data.append(day_data)
    
    # Calcular fechas para navegación
    prev_week_offset = week_offset - 1
    next_week_offset = week_offset + 1
    
    context = {
        'cell': cell,
        'calendar_data': calendar_data,
        'week_start': week_dates[0],
        'week_end': week_dates[-1],
        'workdays': workdays,
        'current_week_offset': week_offset,
        'prev_week_offset': prev_week_offset,
        'next_week_offset': next_week_offset,
        'week_range': f"{week_dates[0].strftime('%d/%m')} - {week_dates[-1].strftime('%d/%m/%Y')}"
    }

    return render(request, 'planning/plannedProduction.html', context)

def addProduction(request):
    if request.method == "POST":
        form = PlannedProductionForm(request.POST)
        formset = ProductionDetailFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            planned = form.save(commit=False)
            planned.created_by = request.user
            planned.save()

            details = formset.save(commit=False)
            for detail in details:
                detail.planned_production = planned
                detail.save()
            return redirect("planningMachineList")
    else:
        form = PlannedProductionForm()
        formset = ProductionDetailFormSet()

    return render(request, 'planning/addProduction.html', {
        "form": form,
        "formset": formset,
    })
    
class downTimeListView(ListView):
    model = Cell
    template_name = 'planning/downTimeList.html'
    context_object_name = 'machines'

def plannedDownTime (request, cell_id):
    cell = get_object_or_404(Cell, pk=cell_id)
    planned_downtime_cells = plannedDownTimeCells.objects.filter(cell=cell).select_related('planned_downtime')
    week_offset = int(request.GET.get('week_offset', 0))
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    target_monday = monday + timedelta(weeks=week_offset)
    month = today.month
    month_name = calendar.month_name[month]
    year = today.year
    cal = calendar.monthcalendar(year, month)
    weekdays = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    workdays = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    start_time = datetime.strptime("06:30", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")
    interval = timedelta(minutes=90)  # 1 hora y media

    week_dates = []
    for i in range(5):  # 5 días laborales
        week_dates.append(target_monday + timedelta(days=i))

    time_slots = []
    current = start_time
    while current < end_time:
        # puedes guardar el inicio y fin de cada intervalo
        time_slots.append({
            "start": current.strftime("%H:%M"),
            "end": (current + interval).strftime("%H:%M")
        })
        current += interval
    
    # Calcular fechas para navegación
    prev_week_offset = week_offset - 1
    next_week_offset = week_offset + 1
     
    context = {
        'cells': cell,
        'downtimes': planned_downtime_cells,
        'today': today.day,
        'month': month_name, 
        'week_start': week_dates[0].strftime("%A %d"),
        'week_end': week_dates[-1].strftime("%A %d"),
        'month_days': cal,
        "weekdays": weekdays,
        'workdays': workdays,
        'year': year,
        'time_slots': time_slots
    }
    return render(request, 'planning/plannedDownTime.html', context)
    
def addDownTime(request):
    if request.method == "POST":
        form = plannedDownTimeForm(request.POST)
        if form.is_valid():
            downtime = form.save(commit=False)
            downtime.created_by = request.user
            downtime.save()

            cells = form.cleaned_data["cells"]
            for cell in cells:
                plannedDownTimeCells.objects.create(
                    planned_downtime=downtime,
                    cell=cell
                )
            return redirect("downTimeList")
    else:
        form = plannedDownTimeForm()

    return render(request, 'planning/addDownTime.html', {
        "form": form,
    })
    
