from django import forms
from .models import Concepto, VersionConcepto
from grupo_concepto.models import GrupoConcepto


class ConceptoAdminForm(forms.ModelForm):
    denominacion = forms.CharField(
        label="Denominación",
        max_length=VersionConcepto._meta.get_field("denominacion").max_length,
        help_text="Ej: Sueldo Basico, Obra Social, etc",
    )

    grupo = forms.ModelChoiceField(
        label="Grupo de concepto",
        queryset=GrupoConcepto.objects.all(),
    )

    codigo_arca = forms.CharField(
        label="Código ARCA",
        max_length=VersionConcepto._meta.get_field("codigo_arca").max_length,
        validators=VersionConcepto._meta.get_field("codigo_arca").validators,
        help_text="Codigo del Concepto de ARCA al que se parametriza el concepto de la empresa",
    )

    categoria = forms.ChoiceField(
        label="Categoría",
        choices=VersionConcepto.Categoria.choices,
    )

    tipo = forms.ChoiceField(
        label="Tipo",
        choices=VersionConcepto.Tipo.choices,
    )

    unidad = forms.ChoiceField(
        label="Unidad",
        choices=VersionConcepto.Unidad.choices,
    )

    class Meta:
        model = Concepto
        fields = [
            'empresa',
            'denominacion',
            'grupo',
            'codigo_arca',
            'categoria',
            'tipo',
            'unidad',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["empresa"].disabled = True

            version = (
                VersionConcepto.objects
                .vigente()
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
                })
