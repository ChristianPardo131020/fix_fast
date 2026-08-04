import http from './http'

export const movimientosCajaApi = {
  list: () => http.get('/movimientos-caja/'),
  create: (payload) => http.post('/movimientos-caja/', payload),
  get: (id) => http.get(`/movimientos-caja/${id}/`),
  remove: (id) => http.delete(`/movimientos-caja/${id}/`),
}
