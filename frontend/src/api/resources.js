import http from './http'

export const dashboardApi = {
  // params: { year, month?, chart_granularity? } — ver
  // backend/app/routes/dashboard_routes.py. Todo lo que pinta el
  // dashboard viene ya calculado en esta unica llamada.
  get: (params) => http.get('/dashboard/', { params }),
}

export const clientesApi = {
  list: () => http.get('/clientes/'),
  create: (payload) => http.post('/clientes/', payload),
  get: (id) => http.get(`/clientes/${id}/`),
  remove: (id) => http.delete(`/clientes/${id}/`),
}

export const ordenesApi = {
  list: () => http.get('/ordenes/'),
  create: (payload) => http.post('/ordenes/', payload),
  get: (id) => http.get(`/ordenes/${id}/`),
  update: (id, payload) => http.put(`/ordenes/${id}/`, payload),
  remove: (id) => http.delete(`/ordenes/${id}/`),
}

export const pagosApi = {
  list: () => http.get('/pagos/'),
  create: (payload) => http.post('/pagos/', payload),
  get: (id) => http.get(`/pagos/${id}/`),
  remove: (id) => http.delete(`/pagos/${id}/`),
}

// Sin auth: lo consulta el cliente final desde /seguimiento.
export const publicApi = {
  trackOrder: (codigo, telefono) => http.get('/publico/seguimiento', { params: { codigo, telefono } }),
}
