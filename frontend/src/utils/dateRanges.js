// Rangos de fecha compartidos entre PeriodFilter (presets del filtro) y
// las vistas que lo usan (Ingresos, Egresos) para arrancar ya
// filtradas por defecto en "Este mes" sin duplicar esta cuenta en cada
// archivo.

export function toISO(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function startOfWeek(date) {
  const d = new Date(date)
  const day = d.getDay() // 0 = domingo .. 6 = sabado
  const diff = (day === 0 ? -6 : 1) - day // retrocede hasta el lunes
  d.setDate(d.getDate() + diff)
  return d
}

export function rangoHoy(hoy = new Date()) {
  return { desde: toISO(hoy), hasta: toISO(hoy) }
}

export function rangoEstaSemana(hoy = new Date()) {
  const inicio = startOfWeek(hoy)
  const fin = new Date(inicio)
  fin.setDate(inicio.getDate() + 6)
  return { desde: toISO(inicio), hasta: toISO(fin) }
}

export function rangoEsteMes(hoy = new Date()) {
  return {
    desde: toISO(new Date(hoy.getFullYear(), hoy.getMonth(), 1)),
    hasta: toISO(new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0)),
  }
}

export function rangoEsteAnio(hoy = new Date()) {
  return {
    desde: toISO(new Date(hoy.getFullYear(), 0, 1)),
    hasta: toISO(new Date(hoy.getFullYear(), 11, 31)),
  }
}
