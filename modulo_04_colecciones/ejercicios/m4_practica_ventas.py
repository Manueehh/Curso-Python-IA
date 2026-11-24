"""Módulo 4 - Práctica 4: análisis de ventas en memoria.

Cada venta es un diccionario con las claves "fecha", "vendedor", "region",
"producto", "categoria", "unidades" y "precio". Ninguna función modifica la
lista de ventas que recibe.
"""

from m4_datos_ventas import VENTAS

ANCHO = 44


def importe(venta: dict) -> float:
    """Devuelve el importe de una venta: unidades por precio, con dos decimales.

    >>> importe({"unidades": 3, "precio": 19.9})
    59.7
    """
    return round(int(venta.get("unidades")) * float(venta.get("precio")),2)


def total_ventas(ventas: list[dict]) -> float:
    """Devuelve la suma de los importes de todas las ventas, con dos decimales."""
    total = 0.0
    for venta in ventas:
        total += importe(venta)
    return total


def filtrar_ventas(ventas: list[dict], *, region: str | None = None,
                   categoria: str | None = None, vendedor: str | None = None,
                   desde: str | None = None, hasta: str | None = None) -> list[dict]:
    """Devuelve las ventas que cumplen todos los criterios indicados.

    Un criterio que vale ``None`` no se aplica. ``desde`` y ``hasta`` son
    fechas ISO y las dos están incluidas en el intervalo.
    """
    resultado = []
    for venta in ventas:
        if region is not None and venta["region"] != region:
            continue
        if categoria is not None and venta["categoria"] != categoria:
            continue
        if vendedor is not None and venta["vendedor"] != vendedor:
            continue
        if desde is not None and venta["fecha"] < desde:
            continue
        if hasta is not None and venta["fecha"] > hasta:
            continue
        resultado.append(venta)
    return resultado
    # Las fechas ISO se pueden comparar como texto: su orden alfabético
    # coincide con el cronológico.


def importe_por(ventas: list[dict], campo: str) -> dict[str, float]:
    """Agrupa las ventas por ``campo`` y devuelve el importe total de cada grupo.

    Los importes van redondeados a dos decimales.

    >>> importe_por([{"region": "Norte", "unidades": 2, "precio": 10.0}], "region")
    {'Norte': 20.0}
    """
    totales = {}
    for venta in ventas:
        grupo = venta[campo]
        totales[grupo] = totales.get(grupo, 0) + importe(venta)
    return {grupo: round(total, 2) for grupo, total in totales.items()}


def unidades_por_producto(ventas: list[dict]) -> dict[str, int]:
    """Devuelve las unidades totales vendidas de cada producto."""
    unidades = {}
    for venta in ventas:
        producto = venta["producto"]
        unidades[producto] = unidades.get(producto, 0) + venta["unidades"]
    return unidades


def ranking(ventas: list[dict], campo: str, cantidad: int = 3) -> list[tuple[str, float]]:
    """Devuelve los ``cantidad`` grupos con mayor importe, como tuplas (clave, importe).

    De mayor a menor importe. A igual importe, por orden alfabético de la clave.
    """
    totales = importe_por(ventas, campo)
    ordenados = sorted(totales.items(), key=lambda par: (-par[1], par[0]))
    return ordenados[:cantidad]


def producto_mas_vendido(ventas: list[dict]) -> str | None:
    """Devuelve el producto con más unidades vendidas, o ``None`` si no hay ventas.

    En caso de empate, el primero por orden alfabético.
    """
    unidades = unidades_por_producto(ventas)
    return min(unidades, key=lambda producto: (-unidades[producto], producto), default=None)


def ticket_medio(ventas: list[dict]) -> float:
    """Devuelve el importe medio por venta, con dos decimales. Sin ventas, 0.0."""
    if not ventas:
        return 0.0
    total = sum(venta["unidades"] * venta["precio"] for venta in ventas)
    return round(total / len(ventas), 2)


def generar_informe(ventas: list[dict]) -> str:
    """Devuelve el informe de ventas como texto, con el formato del enunciado."""
    producto = producto_mas_vendido(ventas) or "-"
    lineas = [
        "=" * ANCHO,
        f"{'INFORME DE VENTAS':^{ANCHO}}",
        "=" * ANCHO,
        f"{'Ventas registradas':<30}{len(ventas):>14}",
        f"{'Importe total':<30}{total_ventas(ventas):>14,.2f}",
        f"{'Ticket medio':<30}{ticket_medio(ventas):>14,.2f}",
        f"{'Producto más vendido':<30}{producto:>14}",
    ]
    for campo, titulo in [("region", "Por región"), ("categoria", "Por categoría"),
                          ("vendedor", "Por vendedor")]:
        lineas.append("-" * ANCHO)
        lineas.append(titulo)
        for clave, total in ranking(ventas, campo, cantidad=None):
            lineas.append(f"  {clave:<28}{total:>14,.2f}")
    lineas.append("=" * ANCHO)
    return "\n".join(lineas)


def main():
    print(generar_informe(VENTAS))
    print()
    print("Solo la región Sur, segunda quincena:")
    print(generar_informe(filtrar_ventas(VENTAS, region="Sur", desde="2026-10-16")))


if __name__ == "__main__":
    main()
