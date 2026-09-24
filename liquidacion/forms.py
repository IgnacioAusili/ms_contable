from django import forms
from django.forms.models import BaseInlineFormSet
from empleado.models import Empleado
from concepto.models import VersionConcepto
from .models import Liquidacion, LiquidacionEmpleado, DetalleLiquidacion


class LiquidacionForm(forms.ModelForm):
    class Meta:
        model = Liquidacion
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Una vez creada, la empresa no se puede cambiar.
        if self.instance and self.instance.pk:
            self.fields["empresa"].disabled = True


class LiquidacionEmpleadoForm(forms.ModelForm):
    class Meta:
        model = LiquidacionEmpleado
        fields = "__all__"
        widgets = {
            "observaciones": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            ),
        }


class LiquidacionEmpleadoInlineForm(forms.ModelForm):
    class Meta:
        model = LiquidacionEmpleado
        fields = "__all__"

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields["empleado"].queryset = Empleado.objects.filter(
                empresa=empresa
            )
        else:
            self.fields["empleado"].queryset = Empleado.objects.none()

        # Una vez creado, el empleado no se puede cambiar.
        if self.instance.pk:
            self.fields["empleado"].disabled = True


class LiquidacionEmpleadoInlineFormSet(BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)

        if self.instance.empresa_id:
            kwargs["empresa"] = self.instance.empresa
        else:
            kwargs["empresa"] = None

        return kwargs


class DetalleLiquidacionForm(forms.ModelForm):
    class Meta:
        model = DetalleLiquidacion
        fields = "__all__"
        widgets = {
            "formula_base": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Una vez creado, no se puede cambiar el concepto.
        if self.instance and self.instance.pk:
            self.fields["concepto"].disabled = True


class DetalleLiquidacionFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        empresa = self.instance.liquidacion.empresa

        queryset = (
            VersionConcepto.objects
            .filter(concepto__empresa=empresa)
            .ultima_version()
        )

        # Si el detalle ya existe, mostrar en base a su versión histórica,
        # aunque el concepto haya sido eliminado. Puede pasar para liquidaciones cerradas
        if form.instance.pk:
            queryset = queryset | (
                VersionConcepto.todos
                .filter(pk=form.instance.concepto_id)
            )

        form.fields["concepto"].queryset = queryset.distinct()
