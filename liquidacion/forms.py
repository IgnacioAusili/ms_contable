from django import forms
from django.forms.models import BaseInlineFormSet

from base_imponible.models import ResultadoBaseImponible
from core.utils import format_decimal_2
from empleado.models import Empleado
from concepto.models import VersionConcepto
from .models import Liquidacion, LiquidacionEmpleado, DetalleLiquidacion
from .services.LiquidacionEmpleadoService import LiquidacionEmpleadoService


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

    def save(self, commit=True):
        liquidaciones_empleado = super().save(commit=commit)

        if commit:
            for liquidacion_empleado in self.new_objects:
                LiquidacionEmpleadoService(
                    liquidacion_empleado
                ).crear()

        return liquidaciones_empleado

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


class ImporteResultadoWidget(forms.NumberInput):
    template_name = "admin/widgets/importe_resultado.html"


class ResultadoBaseImponibleInlineForm(forms.ModelForm):
    importe = forms.DecimalField(
        label="Importe",
        max_digits=20,
        decimal_places=2,
        required=True,
        widget=ImporteResultadoWidget(),
    )

    class Meta:
        model = ResultadoBaseImponible
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.initial["importe"] = format_decimal_2(self.instance.importe)

            if self.instance.base_imponible.identificador == "detracciones":
                self.fields["importe"].widget.attrs["data_sugerencias"] = (
                    "Valores sugeridos: 7003.68 (jornada completa), "
                    "4692.47 (media jornada)"
                )
            else:
                self.fields["importe"].disabled = True
                self.fields["importe"].widget.attrs["class"] = (
                    self.fields["importe"].widget.attrs.get("class", "")
                    + " importe-no-editable"
                )
