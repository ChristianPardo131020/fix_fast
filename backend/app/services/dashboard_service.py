"""
Agregaciones del dashboard operativo.

Toda la logica de calculo (ingresos, utilidad, variaciones contra el
periodo anterior, alertas, etc.) vive aca — el frontend solo pinta lo
que este servicio devuelve, no calcula nada. Las consultas usan
agregaciones de SQL (SUM/COUNT/AVG/GROUP BY) en vez de traer filas
completas a Python cuando es posible, para evitar cargar listas enormes
y evitar N+1.

Convencion de "periodo": year siempre requerido; month es opcional
(None = todo el año). El periodo anterior es el mismo largo (un mes o
un año) inmediatamente antes, para que la comparacion "vs periodo
anterior" sea siempre entre rangos equivalentes.
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.estados import ESTADOS, resolve_estado_key
from app.models.historial_estado import HistorialEstado
from app.models.movimiento_caja import MovimientoCaja
from app.models.orden import Orden
from app.models.pago import Pago

# --- Umbrales de alertas (todas se disparan solas, no hay texto fijo) ---
DIAS_SIN_MOVIMIENTO = 5
DIAS_ATRASADO = 7
DIAS_CARTERA_VENCIDA = 15
GASTOS_ANOMALOS_FACTOR = Decimal("1.3")  # +30% vs el periodo anterior

GRANULARIDADES_VALIDAS = ("day", "week", "month", "year")

_METODOS_CANONICOS = {
    "efectivo": "Efectivo",
    "transferencia": "Transferencia",
    "tarjeta": "Tarjeta",
    "nequi": "Nequi",
    "daviplata": "Daviplata",
}


def _normalizar_metodo(raw: str | None) -> str:
    return _METODOS_CANONICOS.get((raw or "").strip().lower(), "Otros")


def _money(value) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _pct(value) -> Decimal:
    return Decimal(value or 0).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


# --------------------------------------------------------------------------
# Rango de fechas del periodo actual y el anterior (mismo largo)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Periodo:
    inicio: date
    fin: date  # exclusivo
    inicio_anterior: date
    fin_anterior: date  # exclusivo, siempre == inicio
    label: str


_MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def resolver_periodo(year: int, month: int | None, day: int | None = None) -> Periodo:
    if month is None:
        inicio = date(year, 1, 1)
        fin = date(year + 1, 1, 1)
        inicio_anterior = date(year - 1, 1, 1)
        label = f"Todo {year}"
    elif day is None:
        inicio = date(year, month, 1)
        fin = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
        if month == 1:
            inicio_anterior = date(year - 1, 12, 1)
        else:
            inicio_anterior = date(year, month - 1, 1)
        label = f"{_MESES[month - 1]} {year}"
    else:
        inicio = date(year, month, day)
        fin = inicio + timedelta(days=1)
        inicio_anterior = inicio - timedelta(days=1)
        label = f"{day} de {_MESES[month - 1]} {year}"

    return Periodo(inicio=inicio, fin=fin, inicio_anterior=inicio_anterior, fin_anterior=inicio, label=label)


def _variacion(actual: Decimal, anterior: Decimal) -> tuple[Decimal | None, str]:
    """% de cambio de `actual` contra `anterior`. None si no hay base de
    comparacion honesta (periodo anterior en 0), en vez de inventar un
    numero (ej. "infinito" o dividir por cero)."""
    if anterior == 0:
        if actual == 0:
            return Decimal("0.0"), "flat"
        return None, "up"

    variacion = ((actual - anterior) / abs(anterior)) * 100
    tendencia = "up" if variacion > 0 else "down" if variacion < 0 else "flat"
    return _pct(variacion), tendencia


def _metric(actual, anterior) -> dict:
    actual_dec = _money(actual)
    variacion, tendencia = _variacion(Decimal(actual or 0), Decimal(anterior or 0))
    return {"valor": actual_dec, "variacion_pct": variacion, "tendencia": tendencia}


def _metric_int(actual: int, anterior: int) -> dict:
    variacion, tendencia = _variacion(Decimal(actual), Decimal(anterior))
    return {"valor": actual, "variacion_pct": variacion, "tendencia": tendencia}


# --------------------------------------------------------------------------
# Bloques de calculo, cada uno recibe el rango de fechas que necesita
# --------------------------------------------------------------------------

def _estado_counts(db: Session, inicio: date, fin: date) -> dict[str, int]:
    """Cuenta ordenes por estado canonico dentro de [inicio, fin).

    Se agrupa por el string crudo en SQL (GROUP BY, agregado — no trae
    filas de mas) y despues se resuelve cada string a su key canonica en
    Python, porque esa resolucion usa matching por substring (variantes
    legacy) que no es trivial de expresar 1:1 en SQL sin duplicar la
    logica de app/core/estados.py.
    """
    filas = (
        db.query(Orden.estado, func.count(Orden.id))
        .filter(Orden.fecha_ingreso >= inicio, Orden.fecha_ingreso < fin)
        .group_by(Orden.estado)
        .all()
    )

    counts = {estado.key: 0 for estado in ESTADOS}
    for estado_raw, cantidad in filas:
        counts[resolve_estado_key(estado_raw)] += cantidad

    return counts


def _ingresos_egresos(db: Session, inicio: date, fin: date) -> tuple[Decimal, Decimal]:
    pagos = db.query(func.coalesce(func.sum(Pago.valor), 0)).filter(
        Pago.created_at >= inicio, Pago.created_at < fin
    ).scalar()

    otros_ingresos = db.query(func.coalesce(func.sum(MovimientoCaja.valor), 0)).filter(
        MovimientoCaja.tipo == "ingreso", MovimientoCaja.created_at >= inicio, MovimientoCaja.created_at < fin
    ).scalar()

    egresos = db.query(func.coalesce(func.sum(MovimientoCaja.valor), 0)).filter(
        MovimientoCaja.tipo == "egreso", MovimientoCaja.created_at >= inicio, MovimientoCaja.created_at < fin
    ).scalar()

    return Decimal(pagos) + Decimal(otros_ingresos), Decimal(egresos)


def _saldo_pendiente(db: Session, inicio: date, fin: date) -> Decimal:
    total = db.query(func.coalesce(func.sum(Orden.saldo), 0)).filter(
        Orden.fecha_ingreso >= inicio, Orden.fecha_ingreso < fin
    ).scalar()
    return Decimal(total)


def _kpis(db: Session, periodo: Periodo) -> dict:
    ingresos, egresos = _ingresos_egresos(db, periodo.inicio, periodo.fin)
    ingresos_ant, egresos_ant = _ingresos_egresos(db, periodo.inicio_anterior, periodo.fin_anterior)

    utilidad = ingresos - egresos
    utilidad_ant = ingresos_ant - egresos_ant

    margen = (utilidad / ingresos * 100) if ingresos else Decimal(0)
    margen_ant = (utilidad_ant / ingresos_ant * 100) if ingresos_ant else Decimal(0)
    # Para el margen, "variacion_pct" son PUNTOS porcentuales (45% -> 50%
    # es "+5", no "+11%"), porque comparar un % contra otro % en terminos
    # relativos es ilegible y engañoso cuando el margen es chico.
    margen_variacion = _pct(margen - margen_ant)
    margen_tendencia = "up" if margen_variacion > 0 else "down" if margen_variacion < 0 else "flat"

    saldo_pendiente = _saldo_pendiente(db, periodo.inicio, periodo.fin)
    saldo_pendiente_ant = _saldo_pendiente(db, periodo.inicio_anterior, periodo.fin_anterior)

    estados = _estado_counts(db, periodo.inicio, periodo.fin)
    estados_ant = _estado_counts(db, periodo.inicio_anterior, periodo.fin_anterior)

    return {
        "ingresos": _metric(ingresos, ingresos_ant),
        "utilidad": _metric(utilidad, utilidad_ant),
        "margen_pct": {"valor": _pct(margen), "variacion_pct": margen_variacion, "tendencia": margen_tendencia},
        "saldo_pendiente": _metric(saldo_pendiente, saldo_pendiente_ant),
        # "reparacion" ya no es un estado propio (vocabulario reducido a
        # pendiente/listo/entregado/cancelado, ver app/core/estados.py) —
        # equipos "en reparacion" ahora es lo mismo que "pendiente".
        "equipos_reparacion": _metric_int(estados["pendiente"], estados_ant["pendiente"]),
        "equipos_listos": _metric_int(estados["listo"], estados_ant["listo"]),
    }, estados


def _iter_buckets(inicio: date, fin: date, granularidad: str):
    """Fechas de inicio de cada bucket entre [inicio, fin), alineadas
    igual que date_trunc de Postgres, para poder rellenar con 0 los
    buckets sin movimientos (una serie con huecos se ve rota en el
    grafico)."""
    if granularidad == "day":
        actual = inicio
        while actual < fin:
            yield actual
            actual += timedelta(days=1)
    elif granularidad == "week":
        actual = inicio - timedelta(days=inicio.weekday())  # lunes ISO, igual que date_trunc('week', ...)
        while actual < fin:
            yield actual
            actual += timedelta(days=7)
    elif granularidad == "month":
        y, m = inicio.year, inicio.month
        while date(y, m, 1) < fin:
            yield date(y, m, 1)
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    else:  # year
        y = inicio.year
        while date(y, 1, 1) < fin:
            yield date(y, 1, 1)
            y += 1


def _bucketed_sum(db: Session, modelo, columna_valor, columna_fecha, filtros, granularidad: str) -> dict[date, Decimal]:
    filas = (
        db.query(
            func.date_trunc(granularidad, columna_fecha).label("bucket"),
            func.coalesce(func.sum(columna_valor), 0).label("total"),
        )
        .filter(*filtros)
        .group_by("bucket")
        .all()
    )
    return {bucket.date(): Decimal(total) for bucket, total in filas}


def _cashflow(db: Session, periodo: Periodo, granularidad: str) -> dict:
    pagos_por_bucket = _bucketed_sum(
        db, Pago, Pago.valor, Pago.created_at,
        [Pago.created_at >= periodo.inicio, Pago.created_at < periodo.fin], granularidad,
    )
    otros_ingresos_por_bucket = _bucketed_sum(
        db, MovimientoCaja, MovimientoCaja.valor, MovimientoCaja.created_at,
        [MovimientoCaja.tipo == "ingreso", MovimientoCaja.created_at >= periodo.inicio, MovimientoCaja.created_at < periodo.fin],
        granularidad,
    )
    egresos_por_bucket = _bucketed_sum(
        db, MovimientoCaja, MovimientoCaja.valor, MovimientoCaja.created_at,
        [MovimientoCaja.tipo == "egreso", MovimientoCaja.created_at >= periodo.inicio, MovimientoCaja.created_at < periodo.fin],
        granularidad,
    )

    puntos = []
    acumulado = Decimal(0)
    for bucket in _iter_buckets(periodo.inicio, periodo.fin, granularidad):
        ingresos = pagos_por_bucket.get(bucket, Decimal(0)) + otros_ingresos_por_bucket.get(bucket, Decimal(0))
        egresos = egresos_por_bucket.get(bucket, Decimal(0))
        utilidad = ingresos - egresos
        acumulado += utilidad
        puntos.append({
            "fecha": bucket.isoformat(),
            "ingresos": _money(ingresos),
            "egresos": _money(egresos),
            "utilidad": _money(utilidad),
            "utilidad_acumulada": _money(acumulado),
        })

    return {"granularidad": granularidad, "puntos": puntos}


def _orders_breakdown(db: Session, periodo: Periodo, estados_periodo: dict[str, int]) -> dict:
    total = sum(estados_periodo.values())
    por_estado = [
        {"key": estado.key, "label": estado.label, "color": estado.color, "cantidad": estados_periodo[estado.key]}
        for estado in ESTADOS
    ]
    return {"total": total, "por_estado": por_estado}


def _payments_breakdown(db: Session, periodo: Periodo) -> dict:
    pagos_por_metodo = (
        db.query(Pago.metodo_pago, func.count(Pago.id), func.coalesce(func.sum(Pago.valor), 0))
        .filter(Pago.created_at >= periodo.inicio, Pago.created_at < periodo.fin)
        .group_by(Pago.metodo_pago)
        .all()
    )
    ingresos_por_metodo = (
        db.query(MovimientoCaja.metodo_pago, func.count(MovimientoCaja.id), func.coalesce(func.sum(MovimientoCaja.valor), 0))
        .filter(MovimientoCaja.tipo == "ingreso", MovimientoCaja.created_at >= periodo.inicio, MovimientoCaja.created_at < periodo.fin)
        .group_by(MovimientoCaja.metodo_pago)
        .all()
    )

    acumulado: dict[str, dict] = {}
    for metodo_raw, cantidad, monto in [*pagos_por_metodo, *ingresos_por_metodo]:
        label = _normalizar_metodo(metodo_raw)
        bucket = acumulado.setdefault(label, {"cantidad": 0, "monto": Decimal(0)})
        bucket["cantidad"] += cantidad
        bucket["monto"] += Decimal(monto)

    por_metodo = sorted(
        [{"metodo": label, "cantidad": datos["cantidad"], "monto": _money(datos["monto"])} for label, datos in acumulado.items()],
        key=lambda item: item["monto"],
        reverse=True,
    )
    total_monto = sum((item["monto"] for item in por_metodo), Decimal(0))

    return {"total_monto": _money(total_monto), "por_metodo": por_metodo}


def _performance(db: Session, periodo: Periodo) -> dict:
    # Tiempo promedio de reparacion: ordenes ENTREGADAS durante el
    # periodo (por fecha_entrega, no fecha_ingreso), duracion real
    # ingreso->entrega.
    def tiempo_promedio(inicio: date, fin: date) -> Decimal:
        segundos = db.query(
            func.avg(func.extract("epoch", Orden.fecha_entrega - Orden.fecha_ingreso))
        ).filter(
            Orden.fecha_entrega.isnot(None),
            Orden.fecha_entrega >= inicio,
            Orden.fecha_entrega < fin,
        ).scalar()
        return Decimal(segundos or 0) / Decimal(86400)

    tiempo_actual = tiempo_promedio(periodo.inicio, periodo.fin)
    tiempo_anterior = tiempo_promedio(periodo.inicio_anterior, periodo.fin_anterior)

    # Equipos atrasados: EN VIVO (a hoy), no acotado al periodo — es un
    # indicador operativo de "ahora mismo", igual criterio que ya se usa
    # en OrderCard.vue para marcar prioridad "Urgente".
    limite_atraso = datetime.utcnow() - timedelta(days=DIAS_ATRASADO)
    atrasados_ahora = db.query(func.count(Orden.id)).filter(
        ~Orden.estado.ilike("%entreg%"),
        ~Orden.estado.ilike("%cancel%"),
        Orden.fecha_ingreso < limite_atraso,
    ).scalar()

    # Ticket promedio: ingresos del periodo / cantidad de transacciones
    # (pagos + otros ingresos) del mismo periodo.
    def ticket_promedio(inicio: date, fin: date) -> Decimal:
        ingresos, _ = _ingresos_egresos(db, inicio, fin)
        num_pagos = db.query(func.count(Pago.id)).filter(Pago.created_at >= inicio, Pago.created_at < fin).scalar()
        num_otros = db.query(func.count(MovimientoCaja.id)).filter(
            MovimientoCaja.tipo == "ingreso", MovimientoCaja.created_at >= inicio, MovimientoCaja.created_at < fin
        ).scalar()
        transacciones = num_pagos + num_otros
        return (ingresos / transacciones) if transacciones else Decimal(0)

    ticket_actual = ticket_promedio(periodo.inicio, periodo.fin)
    ticket_anterior = ticket_promedio(periodo.inicio_anterior, periodo.fin_anterior)

    # Conversion: de las ordenes que INGRESARON en el periodo (cohorte),
    # que porcentaje ya se entrego. Las que siguen abiertas simplemente
    # todavia no cuentan como conversion (no se descartan del todo, el
    # total_cohorte las sigue incluyendo en el denominador).
    def conversion(inicio: date, fin: date) -> Decimal:
        total_cohorte = db.query(func.count(Orden.id)).filter(
            Orden.fecha_ingreso >= inicio, Orden.fecha_ingreso < fin
        ).scalar()
        if not total_cohorte:
            return Decimal(0)
        entregadas = db.query(func.count(Orden.id)).filter(
            Orden.fecha_ingreso >= inicio, Orden.fecha_ingreso < fin, Orden.estado.ilike("%entreg%")
        ).scalar()
        return Decimal(entregadas) / Decimal(total_cohorte) * 100

    conversion_actual = conversion(periodo.inicio, periodo.fin)
    conversion_anterior = conversion(periodo.inicio_anterior, periodo.fin_anterior)

    _, egresos_actual = _ingresos_egresos(db, periodo.inicio, periodo.fin)
    _, egresos_anterior = _ingresos_egresos(db, periodo.inicio_anterior, periodo.fin_anterior)

    # Saldo disponible: posicion de caja acumulada HISTORICA (todo pago +
    # ingreso - egreso desde siempre hasta hoy), no acotada al periodo —
    # es "cuanta plata tengo disponible ahora", no "cuanta entro este
    # mes" (eso ya es "ingresos"). La variacion compara contra la
    # posicion que tenia al INICIO del periodo elegido, para mostrar
    # cuanto crecio/bajo la caja desde entonces.
    def saldo_disponible_hasta(corte: datetime) -> Decimal:
        pagos = db.query(func.coalesce(func.sum(Pago.valor), 0)).filter(Pago.created_at < corte).scalar()
        ingresos_otros = db.query(func.coalesce(func.sum(MovimientoCaja.valor), 0)).filter(
            MovimientoCaja.tipo == "ingreso", MovimientoCaja.created_at < corte
        ).scalar()
        egresos = db.query(func.coalesce(func.sum(MovimientoCaja.valor), 0)).filter(
            MovimientoCaja.tipo == "egreso", MovimientoCaja.created_at < corte
        ).scalar()
        return Decimal(pagos) + Decimal(ingresos_otros) - Decimal(egresos)

    saldo_disponible_ahora = saldo_disponible_hasta(datetime.utcnow())
    saldo_disponible_inicio_periodo = saldo_disponible_hasta(datetime.combine(periodo.inicio, datetime.min.time()))

    return {
        "tiempo_promedio_reparacion_dias": _metric(tiempo_actual, tiempo_anterior),
        # Sin comparacion honesta posible (ver docstring de la funcion):
        # "atrasados" es un conteo en vivo, no hay snapshot historico del
        # mismo indicador para el periodo anterior.
        "equipos_atrasados": {"valor": atrasados_ahora, "variacion_pct": None, "tendencia": "flat"},
        "ticket_promedio": _metric(ticket_actual, ticket_anterior),
        "conversion_pct": {
            "valor": _pct(conversion_actual),
            "variacion_pct": _pct(conversion_actual - conversion_anterior),
            "tendencia": "up" if conversion_actual > conversion_anterior else "down" if conversion_actual < conversion_anterior else "flat",
        },
        "gastos_periodo": _metric(egresos_actual, egresos_anterior),
        "saldo_disponible": _metric(saldo_disponible_ahora, saldo_disponible_inicio_periodo),
    }


def _alerts(db: Session, periodo: Periodo) -> list[dict]:
    alertas: list[dict] = []
    ahora = datetime.utcnow()

    # 1) Equipos sin movimiento: abiertos, sin cambio de estado (ni
    # ingreso) en mas de DIAS_SIN_MOVIMIENTO dias.
    abiertas = db.query(Orden.id, Orden.fecha_ingreso).filter(
        ~Orden.estado.ilike("%entreg%"), ~Orden.estado.ilike("%cancel%")
    ).all()
    ids_abiertas = [orden_id for orden_id, _ in abiertas]

    ultimos_cambios: dict[int, datetime] = {}
    if ids_abiertas:
        filas = (
            db.query(HistorialEstado.orden_id, func.max(HistorialEstado.created_at))
            .filter(HistorialEstado.orden_id.in_(ids_abiertas))
            .group_by(HistorialEstado.orden_id)
            .all()
        )
        ultimos_cambios = dict(filas)

    limite_sin_movimiento = ahora - timedelta(days=DIAS_SIN_MOVIMIENTO)
    sin_movimiento = [
        orden_id for orden_id, fecha_ingreso in abiertas
        if (ultimos_cambios.get(orden_id) or fecha_ingreso) < limite_sin_movimiento
    ]
    if sin_movimiento:
        alertas.append({
            "tipo": "sin_movimiento",
            "severidad": "alta",
            "titulo": "Equipos sin movimiento",
            "mensaje": f"{len(sin_movimiento)} equipo(s) sin cambios hace mas de {DIAS_SIN_MOVIMIENTO} dias.",
            "cantidad": len(sin_movimiento),
            "monto": None,
        })

    # 2) Ordenes sin diagnostico: ya salieron de "pendiente" pero no
    # tienen diagnostico cargado — hueco de proceso, no de plata.
    sin_diagnostico = db.query(func.count(Orden.id)).filter(
        ~Orden.estado.ilike("%pendiente%"),
        ~Orden.estado.ilike("%recibido%"),
        ~Orden.estado.ilike("%entreg%"),
        ~Orden.estado.ilike("%cancel%"),
        (Orden.diagnostico.is_(None)) | (Orden.diagnostico == ""),
    ).scalar()
    if sin_diagnostico:
        alertas.append({
            "tipo": "sin_diagnostico",
            "severidad": "media",
            "titulo": "Ordenes sin diagnostico",
            "mensaje": f"{sin_diagnostico} orden(es) en proceso sin diagnostico cargado.",
            "cantidad": sin_diagnostico,
            "monto": None,
        })

    # 3) Listas para entregar (recordatorio operativo, en vivo).
    listas = db.query(func.count(Orden.id)).filter(
        Orden.estado.ilike("%listo%") | Orden.estado.ilike("%reparad%")
    ).scalar()
    if listas:
        alertas.append({
            "tipo": "listas_para_entregar",
            "severidad": "baja",
            "titulo": "Listas para entregar",
            "mensaje": f"{listas} equipo(s) esperando que el cliente los retire.",
            "cantidad": listas,
            "monto": None,
        })

    # 4) Cartera vencida: saldo pendiente en ordenes ya entregadas, o
    # ordenes viejas (> DIAS_CARTERA_VENCIDA) que siguen con saldo.
    limite_cartera = ahora - timedelta(days=DIAS_CARTERA_VENCIDA)
    vencidas = db.query(func.count(Orden.id), func.coalesce(func.sum(Orden.saldo), 0)).filter(
        Orden.saldo > 0,
        (Orden.estado.ilike("%entreg%")) | (Orden.fecha_ingreso < limite_cartera),
    ).first()
    cantidad_vencidas, monto_vencido = vencidas
    if cantidad_vencidas:
        alertas.append({
            "tipo": "cartera_vencida",
            "severidad": "alta",
            "titulo": "Cartera vencida",
            "mensaje": f"{cantidad_vencidas} orden(es) con saldo pendiente de cobro atrasado.",
            "cantidad": cantidad_vencidas,
            "monto": _money(monto_vencido),
        })

    # 5) Gastos fuera de lo normal: egresos del periodo vs el anterior.
    _, egresos_actual = _ingresos_egresos(db, periodo.inicio, periodo.fin)
    _, egresos_anterior = _ingresos_egresos(db, periodo.inicio_anterior, periodo.fin_anterior)
    if egresos_anterior > 0 and egresos_actual > egresos_anterior * GASTOS_ANOMALOS_FACTOR:
        alertas.append({
            "tipo": "gastos_anomalos",
            "severidad": "media",
            "titulo": "Gastos fuera de lo normal",
            "mensaje": f"Los egresos de {periodo.label} superan en mas de 30% al periodo anterior.",
            "cantidad": 1,
            "monto": _money(egresos_actual - egresos_anterior),
        })

    return alertas


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def build_dashboard(db: Session, year: int, month: int | None, day: int | None, chart_granularity: str | None) -> dict:
    periodo = resolver_periodo(year, month, day)
    granularidad = chart_granularity if chart_granularity in GRANULARIDADES_VALIDAS else ("day" if month is not None else "month")

    kpis, estados_periodo = _kpis(db, periodo)

    return {
        "periodo": {
            "year": year,
            "month": month,
            "day": day,
            "label": periodo.label,
            "inicio": periodo.inicio.isoformat(),
            "fin": (periodo.fin - timedelta(days=1)).isoformat(),
        },
        "kpis": kpis,
        "cashflow": _cashflow(db, periodo, granularidad),
        "orders": _orders_breakdown(db, periodo, estados_periodo),
        "payments": _payments_breakdown(db, periodo),
        "alerts": _alerts(db, periodo),
        "performance": _performance(db, periodo),
    }
