from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel


class Metric(BaseModel):
    """Un valor monetario/decimal con su variacion vs el periodo anterior."""
    valor: Decimal
    variacion_pct: Optional[Decimal] = None
    tendencia: Literal["up", "down", "flat"] = "flat"


class MetricInt(BaseModel):
    """Igual que Metric pero para conteos enteros."""
    valor: int
    variacion_pct: Optional[Decimal] = None
    tendencia: Literal["up", "down", "flat"] = "flat"


class PeriodoInfo(BaseModel):
    year: int
    month: Optional[int] = None
    label: str
    inicio: str
    fin: str


class KpisResponse(BaseModel):
    ingresos: Metric
    utilidad: Metric
    margen_pct: Metric
    saldo_pendiente: Metric
    equipos_reparacion: MetricInt
    equipos_listos: MetricInt


class CashflowPunto(BaseModel):
    fecha: str
    ingresos: Decimal
    egresos: Decimal
    utilidad: Decimal
    utilidad_acumulada: Decimal


class CashflowResponse(BaseModel):
    granularidad: Literal["day", "week", "month", "year"]
    puntos: list[CashflowPunto]


class EstadoOrdenes(BaseModel):
    key: str
    label: str
    color: str
    cantidad: int


class OrdersResponse(BaseModel):
    total: int
    por_estado: list[EstadoOrdenes]


class MetodoPago(BaseModel):
    metodo: str
    cantidad: int
    monto: Decimal


class PaymentsResponse(BaseModel):
    total_monto: Decimal
    por_metodo: list[MetodoPago]


class Alerta(BaseModel):
    tipo: str
    severidad: Literal["alta", "media", "baja"]
    titulo: str
    mensaje: str
    cantidad: int
    monto: Optional[Decimal] = None


class PerformanceResponse(BaseModel):
    tiempo_promedio_reparacion_dias: Metric
    equipos_atrasados: MetricInt
    ticket_promedio: Metric
    conversion_pct: Metric
    gastos_periodo: Metric
    saldo_disponible: Metric


class DashboardResponse(BaseModel):
    periodo: PeriodoInfo
    kpis: KpisResponse
    cashflow: CashflowResponse
    orders: OrdersResponse
    payments: PaymentsResponse
    alerts: list[Alerta]
    performance: PerformanceResponse
