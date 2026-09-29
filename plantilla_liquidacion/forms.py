from django import forms
from .models import DetallePlantillaLiquidacion


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
