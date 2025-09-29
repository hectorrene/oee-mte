from django.db import models
from core.models import Cell
from manufacturing.models import Production, DownTime, Defect, hourlyProduction
from planning.models import plannedDownTimeCells

class Recap (models.Model):
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE)
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

    @property
    def total_operating_minutes(self):
        from django.db.models import Min, Max

        productions = hourlyProduction.objects.filter(
        production_detail__model_routing__cell=self.cell,
        pieces__gt=0
        ).aggregate(
            first_hour=Min("hour"),
            last_hour=Max("hour")
        )


        first_hour = productions["first_hour"]
        last_hour = productions["last_hour"]

        if first_hour is None or last_hour is None:
            return 0  # No hubo producción ese día

        # Diferencia de horas * 60 minutos
        return (last_hour - first_hour + 1) * 60

    def calculate_metrics(self):
        try:
            self.availability = (self.total_operating_minutes - self.total_downtime_minutes) / self.total_operating_minutes
        except ZeroDivisionError:
            self.availability = 0

        try:
            self.performance = self.total_actual_pieces / self.total_planned_pieces
        except ZeroDivisionError:
            self.performance = 0

        try:
            self.quality = (self.total_actual_pieces - self.total_defects) / self.total_actual_pieces
        except ZeroDivisionError:
            self.quality = 0

        self.oee_percentage = self.availability * self.performance * self.quality * 100
    
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
