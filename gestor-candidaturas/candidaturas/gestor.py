"""Operaciones sobre el conjunto de candidaturas."""

from datetime import date

from .excepciones import CandidaturaDuplicada, CandidaturaNoEncontrada
from .modelos import ESTADOS, INTERESES, Candidatura


class GestorCandidaturas:
    """Contiene las candidaturas y ofrece las operaciones de la aplicación.

    Usa composición: guarda las candidaturas en un diccionario interno por
    identificador. No lee ni escribe ficheros y no usa ``print`` ni ``input``.
    """

    def __init__(self, candidaturas: list[Candidatura] | None = None):
        """Crea el gestor, vacío o con las candidaturas recibidas."""
        self._candidaturas = {c.id: c for c in candidaturas or []}

    def __len__(self) -> int:
        """Devuelve el número de candidaturas."""
        return len(self._candidaturas)

    def __iter__(self):
        """Recorre las candidaturas por orden de identificador."""
        return iter(sorted(self._candidaturas.values(), key=lambda c: c.id))

    def crear(self, empresa: str, puesto: str, *, fuente: str, interes: str = "medio",
              modalidad: str = "", salario: int | None = None, ubicacion: str = "",
              enlace: str = "", notas: str = "", hoy: date | None = None) -> Candidatura:
        """Da de alta una candidatura y la devuelve.

        El identificador es el mayor que exista más uno, o 1 si no hay
        ninguna. La fecha de envío es ``hoy`` o, si no se indica, la fecha
        actual. ``modalidad``, ``salario``, ``ubicacion``, ``enlace`` y
        ``notas`` son opcionales. Si los datos no valen, ``DatoNoValido`` sube sin capturar y
        no se guarda nada.

        Lanza ``CandidaturaDuplicada`` si ya hay una candidatura **activa** a
        la misma empresa y puesto, sin distinguir mayúsculas de minúsculas.
        """
        nueva = Candidatura(
            id=max(self._candidaturas, default=0) + 1,
            empresa=empresa,
            puesto=puesto,
            fuente=fuente,
            fecha_envio=hoy or date.today(),
            interes=interes,
            modalidad=modalidad,
            salario=salario,
            ubicacion=ubicacion,
            enlace=enlace,
            notas=notas,
        )
        if any(_misma_oferta(nueva, c) for c in self.activas()):
            raise CandidaturaDuplicada(nueva.empresa, nueva.puesto)
        self._candidaturas[nueva.id] = nueva
        return nueva

    def obtener(self, identificador: int) -> Candidatura:
        """Devuelve la candidatura con ese identificador.

        Lanza ``CandidaturaNoEncontrada`` si no existe.
        """
        try:
            return self._candidaturas[identificador]
        except KeyError:
            raise CandidaturaNoEncontrada(identificador) from None

    def cambiar_estado(self, identificador: int, nuevo: str,
                       hoy: date | None = None) -> Candidatura:
        """Cambia el estado de una candidatura y la devuelve.

        Delega en ``Candidatura.cambiar_estado``. ``hoy`` es la fecha actual
        si no se indica.
        """
        candidatura = self.obtener(identificador)
        candidatura.cambiar_estado(nuevo, hoy or date.today())
        return candidatura

    def buscar(self, texto: str) -> list[Candidatura]:
        """Devuelve las candidaturas cuya empresa o puesto contienen ``texto``.

        No distingue mayúsculas de minúsculas. Ordenadas por identificador.
        """
        buscado = texto.strip().casefold()
        return [c for c in self
                if buscado in c.empresa.casefold() or buscado in c.puesto.casefold()]

    def filtrar(self, *, estados: list[str] | None = None, fuentes: list[str] | None = None,
                modalidades: list[str] | None = None,
                texto: str | None = None) -> list[Candidatura]:
        """Devuelve las candidaturas que cumplen todos los criterios indicados.

        Un criterio vacío o ``None`` no se aplica. ``estados``, ``fuentes`` y
        ``modalidades`` son listas de valores admitidos; ``texto`` se busca como en
        ``buscar``. Ordenadas por identificador.
        """
        candidatas = self.buscar(texto) if texto else list(self)
        return [c for c in candidatas
                if (not estados or c.estado in estados)
                and (not fuentes or c.fuente in fuentes)
                and (not modalidades or c.modalidad in modalidades)]

    def activas(self) -> list[Candidatura]:
        """Devuelve las candidaturas activas en el orden en que conviene revisarlas.

        Primero las de mayor interés; a igual interés, las enviadas antes; a
        igual fecha, por identificador.
        """
        return sorted(
            (c for c in self if c.activa),
            key=lambda c: (-INTERESES.index(c.interes), c.fecha_envio, c.id),
        )

    def sin_respuesta(self, hoy: date | None = None) -> list[Candidatura]:
        """Devuelve las candidaturas sin respuesta, de la más antigua a la más reciente.

        Usa ``Candidatura.sin_respuesta``. A igual fecha, por identificador.
        """
        hoy = hoy or date.today()
        return sorted((c for c in self if c.sin_respuesta(hoy)),
                      key=lambda c: (c.fecha_envio, c.id))

    def contar_por_estado(self) -> dict[str, int]:
        """Cuenta las candidaturas de cada estado.

        Aparecen **todos** los estados, en el orden de ``ESTADOS``, aunque
        valgan cero.

        >>> GestorCandidaturas().contar_por_estado()["enviada"]
        0
        """
        conteo = dict.fromkeys(ESTADOS, 0)
        for candidatura in self:
            conteo[candidatura.estado] += 1
        return conteo


def _misma_oferta(a: Candidatura, b: Candidatura) -> bool:
    return (a.empresa.casefold(), a.puesto.casefold()) == (b.empresa.casefold(),
                                                           b.puesto.casefold())
