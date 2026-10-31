import csv
import html
from decimal import Decimal, InvalidOperation
from pathlib import Path


def resumir(ruta):
    """Valida las ventas y calcula el total por ciudad."""
    totales = {}
    cantidad = 0

    with open(ruta, encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)

        if lector.fieldnames != ["ciudad", "monto"]:
            raise ValueError(
                "El archivo debe tener las columnas ciudad,monto."
            )

        for numero, fila in enumerate(lector, start=2):
            ciudad = (fila.get("ciudad") or "").strip()

            if None in fila:
                raise ValueError(
                    f"Fila {numero}: hay columnas adicionales."
                )

            if not ciudad:
                raise ValueError(
                    f"Fila {numero}: falta la ciudad."
                )

            try:
                monto = Decimal(fila.get("monto") or "")
            except InvalidOperation:
                raise ValueError(
                    f"Fila {numero}: el monto no es numérico."
                ) from None

            if not monto.is_finite() or monto < 0:
                raise ValueError(
                    f"Fila {numero}: el monto debe ser "
                    "finito y no negativo."
                )

            totales[ciudad] = (
                totales.get(ciudad, Decimal("0")) + monto
            )
            cantidad += 1

    if cantidad == 0:
        raise ValueError("El archivo no contiene ventas.")

    return cantidad, totales


def generar_informe(
    entrada="ventas.csv",
    salida="public/index.html"
):
    """Genera una página HTML con los resultados."""
    cantidad, totales = resumir(entrada)
    total = sum(totales.values(), Decimal("0"))

    filas = ""

    for ciudad, monto in sorted(totales.items()):
        filas += (
            "<tr>"
            f"<td>{html.escape(ciudad)}</td>"
            f"<td>{monto:.2f}</td>"
            "</tr>"
        )

    pagina = f"""<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1">
    <title>Informe de ventas</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 750px;
            margin: 40px auto;
            padding: 0 20px;
            color: #16324f;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            border-bottom: 1px solid #cccccc;
            text-align: left;
        }}
        th {{
            background: #eaf2f8;
        }}
    </style>
</head>
<body>
    <h1>Informe de ventas por ciudad</h1>
    <p>Datos ficticios para una práctica de CI/CD.</p>
    <p>Registros procesados: {cantidad}</p>

    <table>
        <caption>Ventas en bolivianos</caption>
        <thead>
            <tr>
                <th scope="col">Ciudad</th>
                <th scope="col">Ventas (Bs)</th>
            </tr>
        </thead>
        <tbody>
            {filas}
        </tbody>
    </table>

    <h2>Total: Bs {total:.2f}</h2>
</body>
</html>
"""

    destino = Path(salida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(pagina, encoding="utf-8")

    print(
        f"{cantidad} ventas; "
        f"total Bs {total:.2f}; "
        f"informe: {destino}"
    )

    return destino


if __name__ == "__main__":
    generar_informe()
