from django import forms
from django.forms.models import BaseInlineFormSet
from concepto.models import VersionConcepto
from ..models.m_detalles_liquidacion import DetalleLiquidacion


class DetalleLiquidacionForm(forms.ModelForm):
    class Meta:
        model = DetalleLiquidacion
        fields = "__all__"
        widgets = {
            "formula_base": forms.Textarea(
                attrs={
                    "rows": 2,
                    "style": "min-width: 200px; width: 100%; box-sizing: border-box;",
                }
            ),
            "unidades": forms.TextInput(
                attrs={
                    "style": "max-width: 100px;",
                }
            ),
            "cantidad": forms.TextInput(
                attrs={
                    "style": "max-width: 100px;",
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
