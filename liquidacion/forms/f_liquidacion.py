from django import forms
from ..models.m_liquidacion import Liquidacion


class LiquidacionForm(forms.ModelForm):
    class Meta:
        model = Liquidacion
        fields = "__all__"
        widgets = {
            "observaciones": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Una vez creada, la empresa no se puede cambiar.
        if self.instance and self.instance.pk:
            self.fields["empresa"].disabled = True
