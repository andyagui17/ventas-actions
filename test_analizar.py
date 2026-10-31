import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from analizar import generar_informe, resumir


class TestVentas(unittest.TestCase):

    def procesar_ejemplo(self, contenido):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "ventas.csv"
            ruta.write_text(contenido, encoding="utf-8")

            return resumir(ruta)

    def test_suma_por_ciudad(self):
        contenido = (
            "ciudad,monto\n"
            "Cochabamba,100\n"
            "La Paz,80\n"
            "Cochabamba,50\n"
        )

        cantidad, totales = self.procesar_ejemplo(
            contenido
        )

        self.assertEqual(cantidad, 3)
        self.assertEqual(
            totales["Cochabamba"],
            Decimal("150")
        )
        self.assertEqual(
            totales["La Paz"],
            Decimal("80")
        )

    def test_decimales(self):
        contenido = (
            "ciudad,monto\n"
            "La Paz,0.10\n"
            "La Paz,0.20\n"
        )

        _, totales = self.procesar_ejemplo(contenido)

        self.assertEqual(
            totales["La Paz"],
            Decimal("0.30")
        )

    def test_rechaza_datos_invalidos(self):
        ejemplos = [
            "ciudad,monto\nLa Paz,-100\n",
            "ciudad,monto\nLa Paz,hola\n",
            "ciudad,monto\nLa Paz,NaN\n",
            "ciudad,monto\n,100\n",
            "ciudad,monto\nLa Paz\n",
            "ciudad,monto\nLa Paz,100,extra\n",
            "ciudad,monto\n",
            "lugar,precio\nLa Paz,100\n",
        ]

        for contenido in ejemplos:
            with self.subTest(contenido=contenido):
                with self.assertRaises(ValueError):
                    self.procesar_ejemplo(contenido)

    def test_genera_informe(self):
        with tempfile.TemporaryDirectory() as carpeta:
            entrada = Path(carpeta) / "ventas.csv"
            salida = Path(carpeta) / "index.html"

            entrada.write_text(
                "ciudad,monto\n"
                "Cochabamba,100\n"
                "La Paz,200\n",
                encoding="utf-8"
            )

            generar_informe(entrada, salida)

            pagina = salida.read_text(
                encoding="utf-8"
            )

            self.assertIn("Bs 300.00", pagina)
            self.assertIn("Cochabamba", pagina)
            self.assertIn("La Paz", pagina)


if __name__ == "__main__":
    unittest.main()
