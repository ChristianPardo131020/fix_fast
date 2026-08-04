import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('../layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: { name: 'dashboard' } },
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'clientes', name: 'clientes', component: () => import('../views/ClientesView.vue') },
      { path: 'clientes/:id', name: 'cliente-detalle', component: () => import('../views/ClienteDetalleView.vue'), props: true },
      { path: 'ordenes', name: 'ordenes', component: () => import('../views/OrdenesView.vue') },
      { path: 'ordenes/:id', name: 'orden-detalle', component: () => import('../views/OrdenDetalleView.vue'), props: true },
      { path: 'pagos', name: 'pagos', component: () => import('../views/PagosView.vue') },
      { path: 'caja', name: 'caja', component: () => import('../views/CajaView.vue') },
      { path: 'finanzas', redirect: { name: 'caja' } },
      { path: 'configuracion', name: 'configuracion', component: () => import('../views/ConfiguracionView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: { name: 'dashboard' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
