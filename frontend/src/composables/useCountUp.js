import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

/**
 * Anima un número hacia su valor destino al montar (y en cada cambio).
 *
 * Pensado para KPIs que ya llegan formateados como string en es-CO:
 * "$1.234.567", "12%", "3 dias", "1.234". Detecta el formato y re-anima
 * con el mismo estilo. Si no reconoce un número, devuelve el string
 * original sin animar (fallback seguro: nunca rompe el render).
 *
 * Respeta prefers-reduced-motion: en ese caso pinta el valor final de
 * una, sin animación.
 */
const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3)

/** Convierte un número en formato es-CO (coma decimal, punto de miles) a Number. */
function parseEsCO(value) {
  if (typeof value === 'number') return value
  let body = String(value).trim()
  let neg = false
  if (body.startsWith('-')) {
    neg = true
    body = body.slice(1)
  }
  // Queda solo el cuerpo numérico (dígitos, punto y coma).
  body = body.replace(/[^\d.,]/g, '')
  if (!body) return NaN
  // es-CO: coma = decimal, punto = miles.
  if (body.includes(',')) {
    body = body.replace(/\./g, '').replace(/,/g, '.')
  } else {
    body = body.replace(/\./g, '')
  }
  const n = Number(body)
  if (!Number.isFinite(n)) return NaN
  return neg ? -n : n
}

/** Infiere el "estilo" del string para poder re-formatear el número animado. */
function describe(value) {
  const s = String(value)
  let kind = 'number'
  if (s.includes('%')) kind = 'percent'
  else if (/\bdia/.test(s)) kind = 'days'
  else if (/[$€]/.test(s)) kind = 'currency'
  const decimals = (s.match(/[.,](\d+)/) || [])[1]?.length ?? 0
  const negative = /^-/.test(s)
  return { kind, decimals, negative }
}

function render(value, meta) {
  const sign = meta.negative ? '-' : ''
  const abs = Math.abs(value)
  let body
  if (meta.kind === 'currency') {
    body = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 0 }).format(abs)
    return `${sign}$${body}`
  }
  if (meta.kind === 'percent') {
    body = new Intl.NumberFormat('es-CO', {
      minimumFractionDigits: meta.decimals,
      maximumFractionDigits: meta.decimals,
    }).format(abs)
    return `${sign}${body}%`
  }
  if (meta.kind === 'days') {
    body = new Intl.NumberFormat('es-CO', {
      minimumFractionDigits: meta.decimals,
      maximumFractionDigits: meta.decimals,
    }).format(abs)
    return `${sign}${body} dias`
  }
  body = new Intl.NumberFormat('es-CO', { maximumFractionDigits: 0 }).format(abs)
  return `${sign}${body}`
}

export function useCountUp(getTarget, { duration = 800 } = {}) {
  const initialTarget = parseEsCO(getTarget())

  // Primer paint: ya muestra el valor base ("$0", "0%", "0 dias") en vez
  // de un hueco vacío, y la animación arranca de ahí en el siguiente frame.
  let current = 0
  const display = ref(
    Number.isNaN(initialTarget) ? String(getTarget()) : render(0, describe(String(getTarget()))),
  )

  let raf = null

  function stop() {
    if (raf) {
      cancelAnimationFrame(raf)
      raf = null
    }
  }

  function animateTo(to, from, meta) {
    stop()
    const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
    if (reduced) {
      current = to
      display.value = render(to, meta)
      return
    }
    const start = performance.now()
    const delta = to - from
    if (Math.abs(delta) < 1e-9) {
      current = to
      display.value = render(to, meta)
      return
    }
    function tick(now) {
      const progress = Math.min((now - start) / duration, 1)
      current = from + delta * easeOutCubic(progress)
      display.value = render(current, meta)
      if (progress < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
  }

  function refresh() {
    const meta = describe(String(getTarget()))
    const nextTarget = parseEsCO(getTarget())
    if (Number.isNaN(nextTarget)) {
      display.value = String(getTarget())
      return
    }
    // En el primer montaje `current` es 0 → cuenta desde cero; en cambios
    // posteriores arranca del valor ya mostrado y anima la diferencia.
    animateTo(nextTarget, current, meta)
  }

  onMounted(refresh)
  watch(getTarget, () => refresh())
  onBeforeUnmount(stop)

  return display
}
