from django import forms

from base_imponible.models import BaseImponible
from .models import Concepto, VersionConcepto
from grupo_concepto.models import GrupoConcepto


class ConceptoAdminForm(forms.ModelForm):
    denominacion = forms.CharField(
        label="Denominación",
        max_length=VersionConcepto._meta.get_field("denominacion").max_length,
        help_text="Ej: Sueldo Básico, Obra Social, etc.",
    )

    grupo = forms.ModelChoiceField(
        label="Grupo de concepto",
        queryset=GrupoConcepto.objects.all(),
        required=False,
    )

    codigo_arca = forms.CharField(
        label="Código ARCA",
        max_length=VersionConcepto._meta.get_field("codigo_arca").max_length,
        validators=VersionConcepto._meta.get_field("codigo_arca").validators,
        help_text=(
            "Código del concepto de ARCA al que se parametriza "
            "el concepto de la empresa."
        ),
    )

    categoria = forms.ChoiceField(
        label="Categoría",
        choices=VersionConcepto.Categoria.choices,
    )

    tipo = forms.ChoiceField(
        label="Tipo",
        choices=VersionConcepto.Tipo.choices,
    )

    bases_imponibles = forms.ModelMultipleChoiceField(
        label="Bases imponibles",
        queryset=BaseImponible.objects.filter(configurable=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Seleccione las bases imponibles a las que contribuye este concepto.",
    )

    unidad = forms.ChoiceField(
        label="Unidad",
        choices=VersionConcepto.Unidad.choices,
    )

    class Meta:
        model = Concepto
        fields = [
            "empresa",
            "denominacion",
            "grupo",
            "codigo_arca",
            "categoria",
            "tipo",
            "bases_imponibles",
            "unidad",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["empresa"].disabled = True

            version = (
                VersionConcepto.objects
                .ultima_version()
                .filter(concepto=self.instance)
                .first()
            )

            if version:
                self.initial.update({
                    "denominacion": version.denominacion,
                    "codigo_arca": version.codigo_arca,
                    "categoria": version.categoria,
                    "tipo": version.tipo,
                    "unidad": version.unidad,
                    "grupo": version.grupo,
                    "bases_imponibles": version.bases_imponibles.all(),
                })
