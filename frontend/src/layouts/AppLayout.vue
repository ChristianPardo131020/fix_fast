<template>
  <div class="min-h-screen bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
    <aside
      :class="[
        ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        ui.sidebarCollapsed ? 'lg:w-20' : 'lg:w-72',
      ]"
      class="fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200 bg-white/95 shadow-soft transition-all duration-200 dark:border-slate-800 dark:bg-slate-950/95"
    >
      <div class="flex h-16 items-center gap-3 border-b border-slate-100 px-5 dark:border-slate-800" :class="ui.sidebarCollapsed && 'lg:justify-center lg:px-0'">
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white p-1 shadow-sm">
          <img src="/logo-mark.png" alt="FixFast" class="h-full w-full object-contain" />
        </div>
        <div v-if="!ui.sidebarCollapsed">
          <p class="text-sm font-semibold leading-4">FixFast</p>
          <p class="text-xs text-slate-500 dark:text-slate-400">Repair ERP</p>
        </div>
      </div>

      <nav class="flex-1 space-y-5 overflow-y-auto px-3 py-4 scrollbar-thin">
        <div v-for="group in navGroups" :key="group.label || 'root'">
          <p v-if="group.label && !ui.sidebarCollapsed" class="mb-1.5 px-3 text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
            {{ group.label }}
          </p>
          <div class="space-y-0.5">
            <RouterLink
              v-for="item in group.items"
              :key="item.route"
              :to="{ name: item.route }"
              :title="item.name"
              class="relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition"
              :class="[
                isActive(item)
                  ? 'bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-300'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white',
                ui.sidebarCollapsed && 'lg:justify-center',
              ]"
              @click="ui.closeSidebar"
            >
              <span class="absolute inset-y-1 left-0 w-0.5 rounded-full transition-colors" :class="isActive(item) ? 'bg-brand-500' : 'bg-transparent'" />
              <AppIcon :name="item.icon" class="h-5 w-5 shrink-0" />
              <span v-if="!ui.sidebarCollapsed" class="truncate">{{ item.name }}</span>
            </RouterLink>
          </div>
        </div>
      </nav>

      <div class="border-t border-slate-100 p-3 dark:border-slate-800">
        <div v-if="!ui.sidebarCollapsed" class="mb-3 rounded-xl bg-slate-100 p-3 dark:bg-slate-900">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">API activa</p>
          <p class="mt-1 truncate text-sm text-slate-700 dark:text-slate-200">{{ apiUrl }}</p>
        </div>
        <button
          type="button"
          class="hidden w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 lg:flex dark:text-slate-400 dark:hover:bg-slate-900 dark:hover:text-slate-200"
          :class="ui.sidebarCollapsed && 'lg:justify-center'"
          :title="ui.sidebarCollapsed ? 'Expandir menu' : 'Colapsar menu'"
          @click="ui.toggleSidebarCollapsed"
        >
          <AppIcon :name="ui.sidebarCollapsed ? 'chevron-right' : 'chevron-left'" class="h-4 w-4 shrink-0" />
          <span v-if="!ui.sidebarCollapsed">Colapsar menu</span>
        </button>
      </div>
    </aside>

    <div v-if="ui.sidebarOpen" class="fixed inset-0 z-30 bg-slate-950/40 lg:hidden" @click="ui.closeSidebar" />

    <div class="transition-all duration-200" :class="ui.sidebarCollapsed ? 'lg:pl-20' : 'lg:pl-72'">
      <header class="sticky top-0 z-20 flex h-16 items-center justify-between gap-3 border-b border-slate-200 bg-white/85 px-4 backdrop-blur md:px-6 dark:border-slate-800 dark:bg-slate-950/85">
        <button class="shrink-0 rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden dark:text-slate-300 dark:hover:bg-slate-900" type="button" @click="ui.toggleSidebar">
          <AppIcon name="menu" />
        </button>

        <form class="hidden max-w-md flex-1 md:block" @submit.prevent="submitSearch">
          <label class="relative block">
            <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              v-model="topSearch"
              type="search"
              placeholder="Buscar ordenes por cliente, equipo o estado..."
              class="h-10 w-full rounded-full border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:bg-white focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:focus:bg-slate-950"
            />
          </label>
        </form>

        <div class="ml-auto flex items-center gap-2">
          <button class="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900" type="button" title="Cambiar tema" @click="ui.toggleTheme">
            <AppIcon :name="ui.darkMode ? 'sun' : 'moon'" />
          </button>
          <div class="hidden items-center gap-3 rounded-lg border border-slate-200 px-3 py-1.5 md:flex dark:border-slate-800">
            <div class="h-7 w-7 rounded-full bg-brand-600 text-center text-xs font-bold leading-7 text-white">{{ userInitial }}</div>
            <div>
              <p class="text-sm font-medium leading-4">{{ auth.user?.name || 'Usuario' }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ auth.user?.role || '—' }}</p>
            </div>
          </div>
          <button class="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900" type="button" title="Cerrar sesion" @click="auth.logout()">
            <AppIcon name="logout" />
          </button>
        </div>
      </header>

      <main class="mx-auto max-w-7xl px-4 py-6 pb-24 md:px-6 lg:pb-6">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <nav
      class="fixed inset-x-0 bottom-0 z-20 flex items-stretch border-t border-slate-200 bg-white/95 pb-[env(safe-area-inset-bottom)] backdrop-blur lg:hidden dark:border-slate-800 dark:bg-slate-950/95"
    >
      <RouterLink
        v-for="item in bottomNavItems"
        :key="item.route"
        :to="{ name: item.route }"
        class="flex flex-1 flex-col items-center justify-center gap-1 py-2 text-xs font-medium"
        :class="isActive(item) ? 'text-brand-600 dark:text-brand-400' : 'text-slate-500 dark:text-slate-400'"
      >
        <AppIcon :name="item.icon" class="h-5 w-5" />
        {{ item.name }}
      </RouterLink>
      <button
        type="button"
        class="flex flex-1 flex-col items-center justify-center gap-1 py-2 text-xs font-medium text-slate-500 dark:text-slate-400"
        @click="ui.toggleSidebar"
      >
        <AppIcon name="menu" class="h-5 w-5" />
        Menu
      </button>
    </nav>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import { API_BASE_URL } from '../api/http'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()
const apiUrl = API_BASE_URL
const topSearch = ref('')

const navGroups = [
  { label: null, items: [{ name: 'Dashboard', route: 'dashboard', icon: 'dashboard' }] },
  {
    label: 'Operaciones',
    items: [
      { name: 'Ordenes', route: 'ordenes', icon: 'orders' },
      { name: 'Clientes', route: 'clientes', icon: 'users' },
    ],
  },
  {
    label: 'Finanzas',
    items: [
      { name: 'Ingresos', route: 'pagos', icon: 'payments' },
      { name: 'Egresos', route: 'caja', icon: 'trend-down' },
    ],
  },
  {
    label: 'Administracion',
    items: [{ name: 'Configuracion', route: 'configuracion', icon: 'settings' }],
  },
]

// la bottom nav de mobile solo tiene lugar para las secciones de uso
// diario en el mostrador; "Ingresos" (ventas rapidas sin factura) le
// gana el lugar a "Egresos" porque se registra sobre la marcha desde
// el celular, mientras que los egresos suelen cargarse desde el
// escritorio al cierre del dia. Pagos, Egresos y Configuracion quedan
// detras del boton "Menu" (abre el drawer del sidebar completo)
const bottomNavItems = [
  { name: 'Inicio', route: 'dashboard', icon: 'dashboard' },
  { name: 'Ordenes', route: 'ordenes', icon: 'orders' },
  { name: 'Clientes', route: 'clientes', icon: 'users' },
  { name: 'Ingresos', route: 'pagos', icon: 'trend-up' },
]

// rutas hijas que no tienen su propio item de nav (ej. la ficha de un
// cliente o el detalle de una orden) heredan el titulo/seccion e
// indicador activo del item padre
const childRouteParent = { 'cliente-detalle': 'clientes', 'orden-detalle': 'ordenes' }

function isActive(item) {
  const routeName = childRouteParent[route.name] || route.name
  return routeName === item.route
}

const userInitial = computed(() => (auth.user?.name || 'U').charAt(0).toUpperCase())

// Busqueda global del topbar: por ahora solo cubre ordenes (cliente,
// equipo, estado), que es lo que OrdenesView.vue ya filtra localmente.
// Navega con el termino en la query y la vista lo toma como valor
// inicial de su propio buscador.
function submitSearch() {
  const term = topSearch.value.trim()
  if (!term) return
  router.push({ name: 'ordenes', query: { q: term } })
}

onMounted(() => ui.hydrateTheme())
</script>
