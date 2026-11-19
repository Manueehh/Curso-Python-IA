"""Módulo 1 - Ejercicio 3: código con estilo.

La función de abajo funciona, pero ignora PEP 8. Reescríbela siguiendo las
indicaciones del enunciado sin cambiar su comportamiento.
"""

IVA_GENERAL = 21

def precio_final(precio,iva=21,descuento=0):
  """Devuelve el precio con descuento e IVA aplicados, redondeado a 2 decimales.

    Primero aplica el descuento y después el IVA sobre el precio ya descontado.

    Args:
        precio: Precio base.
        iva: Porcentaje de IVA (21 por defecto).
        descuento: Porcentaje de descuento (0 por defecto).

    Returns:
        El precio final redondeado a 2 decimales.
  """
  precio_descontado = precio-precio * descuento / 100
  precio_con_iva = precio_descontado + precio_descontado * iva / 100
  return round(precio_con_iva,2)
