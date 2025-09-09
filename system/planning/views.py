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
from .forms import PlannedProductionForm, ProductionDetailFormSet, plannedDownTimeForm, UploadExcelForm
from django.contrib import messages
import io
import openpyxl

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
    preview_data = None
    errors = []

    if request.method == "POST":
        if "manual_submit" in request.POST:
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

        # Preview de excel
        elif "daily_preview" in request.POST:
            excel_form = UploadExcelForm(request.POST, request.FILES)
            if excel_form.is_valid():
                try:
                    excel_file = request.FILES["file"]
                    df = pd.read_excel(excel_file)
                    
                    # Validar que tenga las columnas necesarias
                    required_columns = ['Fecha', 'Celda', 'Work order', 'Modelo', 'Cantidad']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        errors.append(f"Faltan columnas: {', '.join(missing_columns)}")
                    else:
                        # Procesar los datos para preview
                        processed_data = []
                        for index, row in df.iterrows():
                            try:
                                # Validar que la celda exista
                                cell = Cell.objects.filter(name=row['Celda']).first()
                                if not cell:
                                    errors.append(f"Fila {index + 1}: Celda '{row['Celda']}' no encontrada")
                                    continue
                                
                                # Validar fecha
                                if pd.isna(row['Fecha']):
                                    errors.append(f"Fila {index + 1}: Fecha vacía")
                                    continue
                                
                                # Procesar fecha (puede venir en diferentes formatos)
                                if isinstance(row['Fecha'], str):
                                    try:
                                        date_obj = pd.to_datetime(row['Fecha']).date()
                                    except:
                                        errors.append(f"Fila {index + 1}: Formato de fecha inválido")
                                        continue
                                else:
                                    date_obj = row['Fecha'].date() if hasattr(row['Fecha'], 'date') else row['Fecha']
                                
                                processed_data.append({
                                    'row_number': index + 1,
                                    'fecha': date_obj,
                                    'celda': cell.name,
                                    'celda_id': cell.id,
                                    'work_order': row['Work order'],
                                    'modelo': row['Modelo'],
                                    'cantidad': row['Cantidad'],
                                    'valid': True
                                })
                                
                            except Exception as e:
                                errors.append(f"Fila {index + 1}: Error procesando datos - {str(e)}")
                        
                        preview_data = processed_data
                        
                except Exception as e:
                    errors.append(f"Error leyendo archivo: {str(e)}")

        # Submit de excel
        elif "daily_submit" in request.POST:
            excel_form = UploadExcelForm(request.POST, request.FILES)
            if excel_form.is_valid():
                try:
                    excel_file = request.FILES["file"]
                    df = pd.read_excel(excel_file)
                    
                    successful_saves = 0
                    
                    for index, row in df.iterrows():
                        try:
                            # Obtener la celda
                            cell = Cell.objects.get(name=row['Celda'])
                            
                            # Procesar fecha
                            if isinstance(row['Fecha'], str):
                                date_obj = pd.to_datetime(row['Fecha']).date()
                            else:
                                date_obj = row['Fecha'].date() if hasattr(row['Fecha'], 'date') else row['Fecha']
                            
                            # Crear o obtener la producción planeada
                            planned, created = plannedProduction.objects.get_or_create(
                                cell=cell,
                                date=date_obj,
                                workorder=row['Work order'],
                                defaults={'created_by': request.user}
                            )
                            
                            # Si ya existe y no fue creado, actualizar created_by si es necesario
                            if not created:
                                planned.created_by = request.user
                                planned.save()
                            
                            # Crear el detalle de producción
                            # Aquí necesitas obtener el model_routing basado en el modelo del Excel
                            # Asumiendo que tienes un modelo ModelRouting
                            try:
                                model_routing = ModelRouting.objects.get(name=row['Modelo'])  # Ajusta según tu modelo
                                productionDetail.objects.get_or_create(
                                    planned_production=planned,
                                    model_routing=model_routing,
                                    defaults={'quantity': row['Cantidad']}
                                )
                            except ModelRouting.DoesNotExist:
                                errors.append(f"Fila {index + 1}: Modelo '{row['Modelo']}' no encontrado")
                                continue
                            
                            successful_saves += 1
                            
                        except Cell.DoesNotExist:
                            errors.append(f"Fila {index + 1}: Celda '{row['Celda']}' no encontrada")
                        except Exception as e:
                            errors.append(f"Fila {index + 1}: {str(e)}")
                    
                    if successful_saves > 0:
                        messages.success(request, f"Se guardaron {successful_saves} registros correctamente")
                    
                    if not errors:
                        return redirect("planningMachineList")
                        
                except Exception as e:
                    errors.append(f"Error procesando archivo: {str(e)}")

    else:
        form = PlannedProductionForm()
        formset = ProductionDetailFormSet()
        excel_form = UploadExcelForm()

    return render(request, 'planning/addProduction.html', {
        "form": form,
        "formset": formset,
        "excel_form": excel_form,
        "preview_data": preview_data,
        "errors": errors,
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
    
