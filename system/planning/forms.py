from django import forms
from django.forms import inlineformset_factory
from .models import plannedProduction, productionDetail, plannedDownTime, plannedDownTimeCells
from core.models import Cell

## FORM PARA INGRESAR PRODUCCIÓN PLANEADA
class PlannedProductionForm(forms.ModelForm):
    class Meta:
        model = plannedProduction
        fields = ["cell", "workorder", "date"]
        widgets = {
            "cell": forms.Select(attrs={"class": "form-select"}),
            "workorder": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ingrese el número de la orden de trabajo"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
        }

# ## FORM PARA INGRESAR PRODUCCION POR UN EXCEL
class UploadExcelForm(forms.Form):
    file = forms.FileField(
        label = "Subir archivo",
        widget=forms.FileInput(attrs={
            "class": "form-select",
            "accept": ".xlsx,.xls"})
    )


## FORM PARA INGRESAR LA INFORMACIÓN DE LOS MODELOS
class ProductionDetailForm(forms.ModelForm):
    class Meta:
        model = productionDetail
        fields = ["model_routing", "quantity"]
        widgets = {
            "model_routing": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": 0}),
        }

ProductionDetailFormSet = inlineformset_factory(
    plannedProduction,
    productionDetail,
    form=ProductionDetailForm,
    extra=1,
    can_delete=True
)

class plannedDownTimeForm(forms.ModelForm):
    cells = forms.ModelMultipleChoiceField(
        queryset=Cell.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "pill-secondary"}),  
        required=True,
        label="cells"
    )

    class Meta:
        model = plannedDownTime
        fields = ["name", "description", "start_time", "end_time", "repetition", "valid_from", "valid_to", "cells"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ingrese el nombre del evento"}),
            "description": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ingrese una descripción"}),
            "start_time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "repetition": forms.Select(attrs={"class": "form-input"}), 
            "valid_from": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "valid_to": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
        }