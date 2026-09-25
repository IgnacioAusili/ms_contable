from django import forms
from django.forms.models import BaseInlineFormSet
from base_imponible.models import ResultadoBaseImponible
from core.utils import format_decimal_2
from empleado.models import Empleado
from ..models import TramoSituacionRevista
from ..models.m_liquidacion_empleado import LiquidacionEmpleado
from ..services.LiquidacionEmpleadoService import LiquidacionEmpleadoService


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

    def save_new(self, form, commit=True):
        liquidacion_empleado = super().save_new(form, commit=False,)

        LiquidacionEmpleadoService(liquidacion_empleado).crear(commit=commit)

        return liquidacion_empleado

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)

        if self.instance.empresa_id:
            kwargs["empresa"] = self.instance.empresa
        else:
            kwargs["empresa"] = None

        return kwargs


class TramoSituacionRevistaInlineForm(forms.ModelForm):
    class Meta:
        model = TramoSituacionRevista
        fields = ("dia_inicio",)


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
