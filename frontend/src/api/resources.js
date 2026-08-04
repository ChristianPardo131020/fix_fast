import http from './http'

export const dashboardApi = {
  get: () => http.get('/dashboard/'),
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
