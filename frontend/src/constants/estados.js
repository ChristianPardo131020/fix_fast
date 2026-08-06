// Vocabulario canonico de estados de una orden. Espejo del backend
// (backend/app/core/estados.py) — misma key, label y color, para que el
// donut/badges del dashboard (que ya vienen calculados del backend) y
// las vistas que crean/editan ordenes (que todavia mandan el label como
// texto libre) queden siempre consistentes.
//
// Antes de este archivo esta lista estaba duplicada (con variaciones
// sutiles) en StatusBadge.vue, OrderCard.vue, DashboardView.vue y los
// selects de OrdenesView.vue/OrdenDetalleView.vue. Ahora todos importan
// de aca.

// Vocabulario reducido a proposito (por ahora): "Diagnostico", "Esperando
// repuesto" y "En reparacion" se sacaron del flujo — quedan solo estos 4
// estados de mas alto nivel. Si vuelven a hacer falta, se reinsertan aca
// y en el espejo del backend (backend/app/core/estados.py).
export const ESTADOS = [
  { key: 'pendiente', label: 'Pendiente', color: '#64748b', icon: 'clock' },
  { key: 'listo', label: 'Listo', color: '#22c55e', icon: 'check' },
  { key: 'entregado', label: 'Entregado', color: '#a855f7', icon: 'check' },
  { key: 'cancelado', label: 'Cancelado', color: '#ef4444', icon: 'trash' },
]

// Labels en el orden del flujo de trabajo, listos para usar en un
// <select>. Mismo string que guarda el backend en Orden.estado.
export const ESTADOS_LABELS = ESTADOS.map((estado) => estado.label)

const ALIASES = {
  pendiente: ['pendiente', 'recibido', 'diagnostico', 'repuesto', 'reparacion', 'proceso'],
  listo: ['listo', 'reparad'],
  entregado: ['entreg'],
  cancelado: ['cancel'],
}

/**
 * Resuelve el string libre de una orden (ej. "En reparacion", o
 * variantes legacy como "recibido") a su definicion canonica. Mismo
 * criterio de matching por substring que usa el backend, para que un
 * dato historico se vea igual en toda la app.
 */
export function resolveEstado(raw) {
  const value = (raw || '').toLowerCase().trim()

  for (const estado of ESTADOS) {
    if (ALIASES[estado.key].some((needle) => value.includes(needle))) {
      return estado
    }
  }

  return ESTADOS[0] // fallback: pendiente
}
