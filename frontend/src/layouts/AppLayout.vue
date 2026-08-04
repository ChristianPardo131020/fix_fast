<template>
  <div class="min-h-screen bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
    <aside
      :class="ui.sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
      class="fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200 bg-white/95 transition-transform duration-200 dark:border-slate-800 dark:bg-slate-950/95"
    >
      <div class="flex h-16 items-center gap-3 border-b border-slate-100 px-5 dark:border-slate-800">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-950 text-sm font-bold text-white dark:bg-white dark:text-slate-950">FF</div>
        <div>
          <p class="text-sm font-semibold leading-4">FixFast</p>
          <p class="text-xs text-slate-500 dark:text-slate-400">Repair ERP</p>
        </div>
      </div>

      <nav class="flex-1 space-y-1 px-3 py-4">
        <RouterLink
          v-for="item in navigation"
          :key="item.name"
          :to="{ name: item.route }"
          class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white"
          active-class="bg-slate-950 text-white hover:bg-slate-950 hover:text-white dark:bg-white dark:text-slate-950 dark:hover:bg-white"
          @click="ui.closeSidebar"
        >
          <AppIcon :name="item.icon" />
          {{ item.name }}
        </RouterLink>
      </nav>

      <div class="border-t border-slate-100 p-4 dark:border-slate-800">
        <div class="rounded-xl bg-slate-100 p-3 dark:bg-slate-900">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">API activa</p>
          <p class="mt-1 truncate text-sm text-slate-700 dark:text-slate-200">{{ apiUrl }}</p>
        </div>
      </div>
    </aside>

    <div v-if="ui.sidebarOpen" class="fixed inset-0 z-30 bg-slate-950/40 lg:hidden" @click="ui.closeSidebar" />

    <div class="lg:pl-72">
      <header class="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200 bg-white/85 px-4 backdrop-blur md:px-6 dark:border-slate-800 dark:bg-slate-950/85">
        <div class="flex items-center gap-3">
          <button class="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden dark:text-slate-300 dark:hover:bg-slate-900" type="button" @click="ui.toggleSidebar">
            <AppIcon name="menu" />
          </button>
          <div>
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">{{ currentSection }}</p>
            <h1 class="text-lg font-semibold text-slate-950 dark:text-white">{{ currentTitle }}</h1>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button class="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900" type="button" title="Cambiar tema" @click="ui.toggleTheme">
            <AppIcon name="moon" />
          </button>
          <div class="hidden items-center gap-3 rounded-lg border border-slate-200 px-3 py-1.5 md:flex dark:border-slate-800">
            <div class="h-7 w-7 rounded-full bg-teal-600 text-center text-xs font-bold leading-7 text-white">A</div>
            <div>
              <p class="text-sm font-medium leading-4">{{ auth.user.name }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ auth.user.role }}</p>
            </div>
          </div>
          <button class="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900" type="button" title="Cerrar sesion" @click="auth.logout()">
            <AppIcon name="logout" />
          </button>
        </div>
      </header>

      <main class="mx-auto max-w-7xl px-4 py-6 md:px-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import { API_BASE_URL } from '../api/http'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'

const route = useRoute()
const auth = useAuthStore()
const ui = useUiStore()
const apiUrl = API_BASE_URL

const navigation = [
  { name: 'Dashboard', route: 'dashboard', icon: 'dashboard' },
  { name: 'Clientes', route: 'clientes', icon: 'users' },
  { name: 'Ordenes', route: 'ordenes', icon: 'orders' },
  { name: 'Pagos', route: 'pagos', icon: 'payments' },
  { name: 'Caja', route: 'caja', icon: 'cash' },
  { name: 'Finanzas', route: 'finanzas', icon: 'dashboard' },
  { name: 'Configuracion', route: 'configuracion', icon: 'settings' },
]

const currentItem = computed(() => navigation.find((item) => item.route === route.name) || navigation[0])
const currentSection = computed(() => 'Operaciones')
const currentTitle = computed(() => currentItem.value.name)

onMounted(() => ui.hydrateTheme())
</script>
