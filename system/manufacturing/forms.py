from django import forms
from django.forms import inlineformset_factory
from .models import Defect, DownTime, hourlyProduction, Production
from core.models import modelRouting, Cell
from planning.models import productionDetail, plannedProduction

# =========================================
# Form para ingresar producción planeado
# =========================================
class PlannedProductionForm(forms.ModelForm):
    class Meta:
        model = plannedProduction
        fields = ["workorder", "date"]
        widgets = {
            "workorder": forms.TextInput(attrs={"class": "form-input", "placeholder": "Ingrese el número de la orden de trabajo"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
        }

# =========================================
# Detalles de producción
# =========================================
class ProductionDetailForm(forms.ModelForm):
    class Meta:
        model = productionDetail
        fields = ["model_routing", "quantity"]
        widgets = {
            "model_routing": forms.Select(attrs={"class": "form-select", "name":"part_number"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": 1, "name":"quantity"}),
        }

    def __init__(self, *args, **kwargs):
        self.cell = kwargs.pop('cell', None)
        super().__init__(*args, **kwargs)
        if self.cell:
            self.fields['model_routing'].queryset = modelRouting.objects.filter(cell=self.cell)

# =========================================
# Formset para relacionar detalles con producción planeada
# =========================================
ProductionFormSet = inlineformset_factory(
    plannedProduction,
    productionDetail,
    form=ProductionDetailForm,
    fields=("model_routing", "quantity", ),
    extra=1,  
    can_delete=True,
)

def production_detail_formset_factory(cell):
    return inlineformset_factory(
        plannedProduction,
        productionDetail,
        form=ProductionDetailForm,
        fk_name='planned_production',
        fields=('model_routing', 'quantity'),
        extra=1,
        can_delete=True,
    )