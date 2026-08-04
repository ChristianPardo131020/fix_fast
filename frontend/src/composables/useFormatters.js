export function useFormatters() {
  const currency = new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  })

  const number = new Intl.NumberFormat('es-CO')

  const date = new Intl.DateTimeFormat('es-CO', {
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
    return date.format(new Date(value))
  }

  return { formatCurrency, formatNumber, formatDate }
}
