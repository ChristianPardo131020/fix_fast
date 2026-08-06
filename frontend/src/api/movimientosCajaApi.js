import http from './http'

// Las rutas de detalle (/{id}) del backend NO llevan barra final (ver
// el comentario equivalente en resources.js) -- get/remove con barra
// final disparaban un redirect 307 que en produccion baja de https a
// http y el navegador lo bloquea como mixed content.
export const movimientosCajaApi = {
  list: () => http.get('/movimientos-caja/'),
  create: (payload) => http.post('/movimientos-caja/', payload),
  get: (id) => http.get(`/movimientos-caja/${id}`),
  remove: (id) => http.delete(`/movimientos-caja/${id}`),
}
