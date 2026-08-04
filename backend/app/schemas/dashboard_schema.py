from pydantic import BaseModel
from decimal import Decimal

class DashboardResponse(BaseModel):

    total_clientes: int

    total_ordenes: int

    ordenes_activas: int

    ordenes_entregadas: int

    ingresos_totales: Decimal

    saldo_pendiente: Decimal

    total_pagos: int