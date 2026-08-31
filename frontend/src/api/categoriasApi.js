import http from './http'

export const categoriasApi = {
  list: (tipo) => http.get('/categorias/', { params: tipo ? { tipo } : {} }),
  create: (payload) => http.post('/categorias/', payload),
  remove: (id) => http.delete(`/categorias/${id}`),
}
