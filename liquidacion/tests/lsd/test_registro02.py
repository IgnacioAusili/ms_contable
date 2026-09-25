from django.test import SimpleTestCase
from datetime import date
from liquidacion.lsd.registro02 import DatosRegistro02, FormaPago, GeneradorRegistro02


class TestGeneradorRegistro02(SimpleTestCase):
    def datos_registro(self, **kwargs):
        datos = {
            "cuil_trabajador": "33693450239",
            "legajo_trabajador": "123",
            "dependencia_revista_trabajador": "Administración",
            "cbu_acreditacion_pago": "0000003100001203173337",
            "cantidad_dias_tope": 30,
            "fecha_pago": date(2026, 9, 30),
            "fecha_rubrica": None,
            "forma_pago": FormaPago.EFECTIVO,
        }
        datos.update(kwargs)
        return DatosRegistro02(**datos)

    def test_generar(self):
        casos = [
            (
                "efectivo",
                {},
                "02336934502390000000123Administración                                    000000310000120317333703020260930        1",
            ),
            (
                "acreditación en cuenta",
                {
                    "legajo_trabajador": "A-123",
                    "dependencia_revista_trabajador": "",
                    "cantidad_dias_tope": 5,
                    "fecha_rubrica": date(2026, 10, 2),
                    "forma_pago": FormaPago.ACREDITACION_EN_CUENTA,
                },
                "023369345023900000A-123                                                  000000310000120317333700520260930202610023",
            ),
            (
                "cheque sin legajo",
                {
                    "legajo_trabajador": "",
                    "dependencia_revista_trabajador": "Planta Permanente",
                    "cantidad_dias_tope": 0,
                    "forma_pago": FormaPago.CHEQUE,
                },
                "02336934502390000000000Planta Permanente                                 000000310000120317333700020260930        2",
            ),
            (
                "pago externo",
                {
                    "legajo_trabajador": "LEGAJO99",
                    "dependencia_revista_trabajador": "Sucursal General Pico",
                    "cbu_acreditacion_pago": "",
                    "cantidad_dias_tope": 999,
                    "fecha_pago": date(2026, 9, 16),
                    "forma_pago": FormaPago.PAGO_EXTERNO,
                },
                "023369345023900LEGAJO99Sucursal General Pico                                                   99920260916        4",
            ),
        ]

        for nombre, cambios, esperado in casos:
            with self.subTest(nombre):
                datos = self.datos_registro(**cambios)
                registro = GeneradorRegistro02(datos).generar()

                self.assertEqual(registro, esperado)

    def test_cbu_obligatorio(self):
        cambios = {
            "cbu_acreditacion_pago": None,
            "forma_pago": FormaPago.ACREDITACION_EN_CUENTA,
        }

        datos = self.datos_registro(**cambios)

        self.assertRaises(Exception, lambda: GeneradorRegistro02(datos).generar())
