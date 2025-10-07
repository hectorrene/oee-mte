from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from core.models import Cell
from .models import Recap
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Avg, Sum

# =========================================
# Lista máquinas dashborads
# =========================================
class machineListView(ListView):
    model = Cell
    template_name = 'analytics/analyticsList.html'
    context_object_name = 'machines'

# =========================================
# Obtiene el lunes y domingo
# =========================================
def weekRange(date=None):
    if date is None:
        date = datetime.now()
    
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    
    return start, end

# =========================================
# Dashboard máquina 
# =========================================
def machineDashboard (request, cell_id):
    cell = get_object_or_404(Cell, id=cell_id)
    today = timezone.now().date()
    start, end = weekRange()
    
    weeklyRecaps = Recap.objects.filter(
        pub_date__gte=start, 
        pub_date__lte=end,
        cell_id=cell_id,
    )

    weeklyMetrics = weeklyRecaps.aggregate(
        wk_availability = Avg("availability"), 
        wk_performance = Avg("performance"),
        wk_quality = Avg("quality"),
        sum_planned_pieces = Sum("total_planned_pieces"),
        sum_actual_pieces = Sum("total_actual_pieces"),
    )

    wk_availability = weeklyMetrics["wk_availability"] or 0
    wk_performance = weeklyMetrics["wk_performance"] or 0 
    wk_quality = weeklyMetrics["wk_quality"] or 0
    sum_planned_pieces = weeklyMetrics["sum_planned_pieces"] or 0
    sum_total_pieces = weeklyMetrics["sum_actual_pieces"] or 0

    monthlyRecaps = Recap.objects.filter(
        cell_id=cell_id,
        pub_date__year=timezone.now().year,
        pub_date__month=timezone.now().month
    )

    monthlyMetrics = monthlyRecaps.aggregate(
        avg_availability=Avg("availability"),
        avg_performance=Avg("performance"),
        avg_quality=Avg("quality"),
    )

    avg_availability = monthlyMetrics["avg_availability"] or 0
    avg_performance = monthlyMetrics["avg_performance"] or 0
    avg_quality = monthlyMetrics["avg_quality"] or 0

    weekly_oee = wk_availability * wk_performance * wk_quality * 100
    monthly_oee = avg_availability * avg_performance * avg_quality * 100
    if sum_planned_pieces > 0:
        completion_percentage = (sum_total_pieces * 100) / sum_planned_pieces
    else:
        completion_percentage = 0
    
    context = {
        "avg_availability": round(avg_availability * 100, 2),
        "avg_performance": round(avg_performance * 100, 2),
        "avg_quality": round(avg_quality * 100, 2),
        "sum_planned_pieces": sum_planned_pieces,
        "sum_total_pieces": sum_total_pieces,
        "wk_availability": round(wk_availability * 100, 2),
        "wk_performance": round(wk_performance * 100, 2),
        "wk_quality": round(wk_quality * 100, 2),
        "completion_percentage": round(completion_percentage, 1),
        "month": round(monthly_oee, 2),
        "week": round(weekly_oee, 2),
    }
    
    return render(request, 'analytics/machineDashboard.html', context)

