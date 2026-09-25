from django.test import SimpleTestCase

from liquidacion.lsd.registro06 import (
    DatosRegistro06,
    GeneradorRegistro06,
)


class TestGeneradorRegistro06(SimpleTestCase):
    def datos_registro(self, **kwargs):
        datos = {
            "cuil_trabajador": "33693450239",
            "observaciones": "Observación de prueba",
        }

        datos.update(kwargs)
        return DatosRegistro06(**datos)

    def test_generar(self):
        casos = [
            (
                "original",
                {},
                "063369345023900000000000000000000000000000000000000000000000000000000000Observación de prueba",
            ),
            (
                "observacion_exactamente_80_caracteres",
                {
                    "observaciones": "A" * 80,
                },
                "0633693450239AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            ),
            (
                "observacion_con_caracteres_especiales",
                {
                    "observaciones": "Licencia: art. 208 LCT - período 01/09/2026",
                },
                "06336934502390000000000000000000000000000000000000Licencia: art. 208 LCT - período 01/09/2026",
            ),
        ]

        for nombre, cambios, esperado in casos:
            with self.subTest(nombre):
                datos = self.datos_registro(**cambios)
                registro = GeneradorRegistro06(datos).generar()

                self.assertEqual(registro, esperado)

    def test_datos_invalidos(self):
        casos = [
            (
                "observacion_vacia",
                {
                    "observaciones": "",
                }
            ),
            (
                "observacion_tope",
                {
                    "observaciones": "A" * 82,
                }
            ),
        ]

        for nombre, cambios in casos:
            with self.subTest(nombre):
                datos = self.datos_registro(**cambios)

                self.assertRaises(Exception, lambda: GeneradorRegistro06(datos).generar())

