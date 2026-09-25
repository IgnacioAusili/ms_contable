from dataclasses import fields
import typing


def validar_datos_obligatorios_dataclass(datos):
    obligatorios_faltantes = datos_obligatorios_faltantes_dataclass(datos)

    if obligatorios_faltantes:
        raise Exception(  # TODO - definir mejor el tipo de excepcion
            "Falta definir datos que son obligatorios."
        )


def datos_obligatorios_faltantes_dataclass(datos):
    """
    Valida que los campos obligatorios de una dataclass estén presentes.
    """
    faltantes = []
    hints = typing.get_type_hints(type(datos))

    for f in fields(datos):
        valor = getattr(datos, f.name)
        tipo = hints[f.name]
        es_opcional = type(None) in typing.get_args(tipo)

        if valor is None and not es_opcional:
            faltantes.append(f.name)

    return faltantes
