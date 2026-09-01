/**
 * Parsea un timestamp de Supabase (CURRENT_TIMESTAMP, que guarda UTC)
 * garantizando que JavaScript lo interprete como UTC.
 *
 * Sin esta función, un string como "2026-09-02T00:30:00" (sin "Z") se
 * interpreta como hora LOCAL — y un registro de las 7:30 PM Colombia
 * aparece en el día siguiente.
 */
export function parseUTC(value) {
  if (!value) return null
  const s = String(value)
  if (s.includes('T') && !s.endsWith('Z') && !/[+-]\d{2}:\d{2}$/.test(s)) {
    return new Date(s + 'Z')
  }
  return new Date(s)
}

export function useFormatters() {
  const currency = new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  })

  const number = new Intl.NumberFormat('es-CO')

  const dateFmt = new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })

  function formatCurrency(value) {
    return currency.format(Number(value || 0))
  }

  function formatNumber(value) {
    return number.format(Number(value || 0))
  }

  function formatDate(value) {
    if (!value) return 'Sin fecha'
    return dateFmt.format(parseUTC(value))
  }

  return { formatCurrency, formatNumber, formatDate, parseUTC }
}
