from django.db import models
from core.models import Cell
from manufacturing.models import Production, DownTime, Defect
from planning.models import plannedDownTimeCells

class Recap (models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    downtime = models.ForeignKey(DownTime, on_delete=models.CASCADE)
    defect = models.ForeignKey(Defect, on_delete=models.CASCADE)
    planned_downtime_cells = models.ForeignKey(plannedDownTimeCells, on_delete=models.CASCADE)
    total_planned_pieces = models.IntegerField()
    total_actual_pieces = models.IntegerField()
    total_downtime_minutes = models.IntegerField()
    total_defects = models.IntegerField()
    availability = models.FloatField()
    performance = models.FloatField()
    quality = models.FloatField()
    oee_percentage = models.FloatField()
    comments = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    
    def _str__(self):
        return f"{self.cell.name} - {self.pub_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        verbose_name_plural = "Recaps"

class OEE(models.Model):
    recap = models.ForeignKey(Recap, on_delete=models.CASCADE)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
    period_type = models.CharField(max_length=50, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ])
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    class Meta:
        verbose_name_plural = "Historial OEE"
