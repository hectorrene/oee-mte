from django.db import models
from planning.models import productionDetail
from core.models import Cause, Cell, Model
from django.contrib.auth.models import User

class Defect(models.Model):
    cause = models.ForeignKey(Cause, on_delete=models.PROTECT, null=True, blank=True)
    production_detail = models.ForeignKey(productionDetail, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    date = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True, choices=[
        ('scrap', 'Scrap'),
        ('rework', 'Retrabajo'),
        ('quality', 'Calidad'),
    ])
    comments = models.TextField(null=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def model(self):
        if self.production_detail:
            return self.production_detail.model_routing.model
        return None
    
    @property
    def cell(self):
        if self.production_detail:
            return self.production_detail.model_routing.cell
        return None

    def __str__(self):
        if self.cell and self.model:
            return f"{self.cell.name} - {self.model.name} - {self.quantity} pcs"
        return f"Defecto - {self.quantity} pcs"
    
    class Meta:
        verbose_name_plural = "Defectos"

class DownTime(models.Model):  
    production_detail = models.ForeignKey(productionDetail, on_delete=models.PROTECT, null=True, blank=True)
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def duration_minutes(self):
        if self.start and self.end:
            delta = self.end - self.start
            return delta.total_seconds() / 60
        return 0
    
    @property
    def cell(self):
        if self.production_detail:
            return self.production_detail.model_routing.cell
        return None

    def __str__(self):
        if self.cell and self.start and self.end:
            return f"{self.cell.name} || de {self.start.strftime('%H:%M')} a {self.end.strftime('%H:%M')}"
        return "Tiempo muerto"
    
    class Meta:
        verbose_name_plural = "Tiempos muertos"

class hourlyProduction(models.Model):  
    hour = models.IntegerField()
    pieces = models.IntegerField()
    production_detail = models.ForeignKey(productionDetail, on_delete=models.PROTECT) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Hora {self.hour}: {self.pieces} piezas"

class Production(models.Model):
    hrxhr = models.ForeignKey(hourlyProduction, on_delete=models.PROTECT, null=True, blank=True)
    production = models.IntegerField(default=0)
    cycle = models.IntegerField(default=1)
    comments = models.TextField(null=True, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.production_detail:
            cell_name = self.production_detail.model_routing.cell.name
            return f"{cell_name} - {self.pub_date.strftime('%Y-%m-%d %H:%M')} - {self.production} pcs"
        return f"Producción - {self.production} pcs"
    
    class Meta:
        verbose_name_plural = "Producción"