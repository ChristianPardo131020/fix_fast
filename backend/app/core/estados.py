"""
Vocabulario canonico de estados de una Orden.

Orden.estado sigue siendo un string libre en la base (ver
app/models/orden.py) — no se migra a un enum de Postgres para no romper
filas historicas ni forzar una migracion. Este modulo es la UNICA fuente
de verdad sobre que estados existen, en que orden van, que color les
corresponde y como se agrupan strings legacy/variantes hacia una key
canonica. Antes de este modulo esa logica de matching estaba duplicada
en el frontend (StatusBadge.vue, DashboardView.vue, OrderCard.vue); acá
vive una sola vez del lado del backend, que es quien calcula los
agregados del dashboard.

Vocabulario reducido a proposito (por ahora): "Diagnostico", "Esperando
repuesto" y "En reparacion" se sacaron del flujo — quedan solo los 4
estados de mas alto nivel. Si vuelven a hacer falta, se reinsertan aca
y en el espejo del frontend (frontend/src/constants/estados.js), nada
mas depende de la lista completa.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EstadoDef:
    key: str        # identificador estable para JSON (frontend, alertas, etc.)
    label: str       # valor humano que se guarda en Orden.estado
    color: str        # hex, usado en donut/badges para que todo coincida


ESTADOS: tuple[EstadoDef, ...] = (
    EstadoDef("pendiente", "Pendiente", "#64748b"),
    EstadoDef("listo", "Listo", "#22c55e"),
    EstadoDef("entregado", "Entregado", "#a855f7"),
    EstadoDef("cancelado", "Cancelado", "#ef4444"),
)

ESTADOS_POR_KEY = {estado.key: estado for estado in ESTADOS}

# Substrings (en minuscula) que identifican cada estado a partir del
# string libre guardado en la base, incluyendo variantes legacy:
# "recibido" era el default viejo de la columna antes de este rediseño,
# y "pagado" viene de un bug ya corregido en pago_routes.py que confundia
# "saldo pagado" con el estado operativo de la orden.
_ALIASES: dict[str, tuple[str, ...]] = {
    "pendiente": ("pendiente", "recibido", "diagnostico", "repuesto", "reparacion", "proceso"),
    "listo": ("listo", "reparad"),
    "entregado": ("entreg",),
    "cancelado": ("cancel",),
}

# Estados "abiertos": una orden en cualquiera de estos todavia esta en
# proceso en el taller (no se fue con el cliente ni se descarto).
ESTADOS_ABIERTOS: tuple[str, ...] = ("pendiente", "listo")


def resolve_estado_key(raw: str | None) -> str:
    """Convierte el string libre de Orden.estado a una key canonica.

    Recorre ESTADOS en orden (que es el orden real del flujo de trabajo)
    y usa matching por substring, igual criterio que ya usaba el
    frontend. Un valor desconocido (dato legacy no contemplado) cae en
    "pendiente" como fallback honesto, mismo comportamiento que tenia
    StatusBadge.vue.
    """
    value = (raw or "").strip().lower()

    for estado in ESTADOS:
        if any(needle in value for needle in _ALIASES[estado.key]):
            return estado.key

    return "pendiente"
