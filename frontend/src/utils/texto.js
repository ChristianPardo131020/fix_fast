/**
 * Normaliza texto para comparación y búsqueda tolerante (Ley de Postel):
 * - minúsculas
 * - sin tildes/acentos (batería === bateria)
 * - sin espacios en los extremos
 *
 * Con esto "Batería", "BATERIA" y "bateria" matchean igual al buscar
 * clientes, órdenes, productos o movimientos de caja.
 */
export function normalizarTexto(value) {
  return String(value ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}
