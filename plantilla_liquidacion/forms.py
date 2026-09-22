from django import forms
from django.forms.models import BaseInlineFormSet
from django.db.models import OuterRef, Subquery
from .models import DetallePlantillaLiquidacion
from concepto.models import VersionConcepto


class DetallePlantillaLiquidacionForm(forms.ModelForm):
    class Meta:
        model = DetallePlantillaLiquidacion
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


class DetallePlantillaLiquidacionFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        if self.instance and self.instance.pk:
            empresa = self.instance.empresa

            ultima_version = (
                VersionConcepto.objects
                .filter(concepto=OuterRef("concepto"))
                .order_by("-version")
                .values("pk")[:1]
            )

            form.fields["concepto"].queryset = (
                VersionConcepto.objects
                .filter(
                    concepto__empresa=empresa,
                    pk=Subquery(ultima_version),
                )
            )
