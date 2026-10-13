from django import forms
from concepto.models import Concepto
from core.forms import DecimalInputField
from .models import DetallePlantillaLiquidacion


class DetallePlantillaLiquidacionForm(forms.ModelForm):
    unidades = DecimalInputField(
        max_digits=DetallePlantillaLiquidacion._meta.get_field("unidades").max_digits,
        decimal_places=DetallePlantillaLiquidacion._meta.get_field("unidades").decimal_places,
        widget=forms.TextInput(
            attrs={
                "style": "max-width: 100px;",
            }
        ),
        help_text=DetallePlantillaLiquidacion._meta.get_field("unidades").help_text,
    )

    class Meta:
        model = DetallePlantillaLiquidacion
        fields = "__all__"
        widgets = {
            "formula_base": forms.Textarea(
                attrs={
                    "rows": 2,
                    "style": "min-width: 200px; width: 100%; box-sizing: border-box;",
                }
            ),
        }

    class Media:
        js = ("core/js/decimal_input.js",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Una vez creado, no se puede cambiar el concepto.
        if self.instance and self.instance.pk:
            self.fields["concepto"].disabled = True

            concepto = Concepto.objects.get(pk=self.instance.concepto.id).versiones.ultima()

            if concepto.codigo_arca:
                self.fields["debito_credito"].required = True

    def clean_debito_credito(self):
        concepto_form = self.cleaned_data["concepto"]
        debito_credito = self.cleaned_data["debito_credito"]

        if concepto_form:
            concepto = Concepto.objects.get(pk=concepto_form.id).versiones.ultima()

            if concepto.codigo_arca and not debito_credito:
                raise forms.ValidationError(
                    "Este campo es obligatorio para conceptos que tienen asociado un código de ARCA."
                )

        return debito_credito
