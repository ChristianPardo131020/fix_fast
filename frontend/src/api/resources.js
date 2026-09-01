import http from './http'

export const dashboardApi = {
  // params: { year, month?, chart_granularity? } — ver
  // backend/app/routes/dashboard_routes.py. Todo lo que pinta el
  // dashboard viene ya calculado en esta unica llamada.
  get: (params) => http.get('/dashboard/', { params }),
}

// Las rutas de detalle (/{id}) del backend NO llevan barra final -- solo
// list()/create() la llevan, porque esas si estan definidas como "/" en
// FastAPI. Pedir "/clientes/5/" contra una ruta "/clientes/{id}" dispara
// un redirect 307 que en algunos proxies (el de Vite en dev, por
// ejemplo) resuelve mal el host y devuelve HTML en vez del JSON
// esperado -- de ahi que el detalle de una orden se viera vacio.
export const clientesApi = {
  list: () => http.get('/clientes/'),
  create: (payload) => http.post('/clientes/', payload),
  get: (id) => http.get(`/clientes/${id}`),
  update: (id, payload) => http.put(`/clientes/${id}`, payload),
  remove: (id) => http.delete(`/clientes/${id}`),
}

export const ordenesApi = {
  list: () => http.get('/ordenes/'),
  create: (payload) => http.post('/ordenes/', payload),
  get: (id) => http.get(`/ordenes/${id}`),
  update: (id, payload) => http.put(`/ordenes/${id}`, payload),
  remove: (id) => http.delete(`/ordenes/${id}`),
  historial: (id) => http.get(`/ordenes/${id}/historial`),
  listRepuestos: (id) => http.get(`/ordenes/${id}/repuestos`),
  addRepuesto: (id, payload) => http.post(`/ordenes/${id}/repuestos`, payload),
  removeRepuesto: (id, repuesto_id) => http.delete(`/ordenes/${id}/repuestos/${repuesto_id}`),
}

export const pagosApi = {
  list: () => http.get('/pagos/'),
  create: (payload) => http.post('/pagos/', payload),
  get: (id) => http.get(`/pagos/${id}`),
  remove: (id) => http.delete(`/pagos/${id}`),
}

// Sin auth: lo consulta el cliente final desde /seguimiento.
export const publicApi = {
  trackOrder: (codigo, telefono) => http.get('/publico/seguimiento', { params: { codigo, telefono } }),
}

export const inventarioApi = {
  listCategorias: () => http.get('/inventario/categorias'),
  createCategoria: (payload) => http.post('/inventario/categorias', payload),
  listProveedores: () => http.get('/inventario/proveedores'),
  createProveedor: (payload) => http.post('/inventario/proveedores', payload),
  listProductos: () => http.get('/inventario/productos'),
  createProducto: (payload) => http.post('/inventario/productos', payload),
  updateProducto: (id, payload) => http.put(`/inventario/productos/${id}`, payload),
  removeProducto: (id) => http.delete(`/inventario/productos/${id}`),
  listMovimientos: (producto_id) => http.get('/inventario/movimientos', { params: { producto_id } }),
  registrarMovimiento: (payload) => http.post('/inventario/movimientos', payload),
  listarBajoStock: () => http.get('/inventario/productos/bajo_stock'),
  registrarCompra: (payload) => http.post('/inventario/compras', payload),
  registrarVenta: (payload) => http.post('/inventario/ventas', payload),
}
