<template>
  <div class="space-y-6">
    <PageHeader title="Configuración">
      <template #eyebrow>
        <span class="rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-brand-700 dark:bg-brand-500/15 dark:text-brand-300">Administración</span>
      </template>
      Personaliza las categorías de ingresos y egresos de tu taller para un control más preciso de tus finanzas, o gestiona tus preferencias de apariencia.
    </PageHeader>

    <div class="grid gap-6 md:grid-cols-3">
      <!-- CATEGORIAS DE INGRESOS -->
      <BaseCard title="Categorías de Ingreso" subtitle="Ventas, servicios rápidos, accesorios, etc.">
        <form @submit.prevent="addCategoria('ingreso')" class="mb-6 flex gap-2">
          <input
            v-model="newIngreso"
            type="text"
            required
            placeholder="Ej. Venta, Accesorio, Pila"
            class="h-10 flex-1 rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
          />
          <BaseButton type="submit" icon="plus" :loading="savingIngreso">Agregar</BaseButton>
        </form>

        <div v-if="loading" class="space-y-2 animate-pulse">
          <div v-for="n in 3" :key="n" class="h-10 rounded-lg bg-slate-100 dark:bg-slate-800" />
        </div>

        <div v-else-if="ingresos.length" class="divide-y divide-slate-100 dark:divide-slate-800/60 max-h-80 overflow-y-auto pr-1">
          <div v-for="cat in ingresos" :key="cat.id" class="flex items-center justify-between py-3">
            <span class="text-sm font-medium capitalize text-slate-700 dark:text-slate-200">{{ cat.nombre }}</span>
            <BaseButton
              variant="ghost"
              size="sm"
              icon="trash"
              @click="removeCategoria(cat)"
            >
              Eliminar
            </BaseButton>
          </div>
        </div>
        <EmptyState
          v-else
          icon="trend-up"
          title="Sin categorías"
          description="Crea categorías para clasificar tus ingresos de mostrador."
        />
      </BaseCard>

      <!-- CATEGORIAS DE EGRESOS -->
      <BaseCard title="Categorías de Egreso" subtitle="Arriendo, servicios, repuestos, empleados, etc.">
        <form @submit.prevent="addCategoria('egreso')" class="mb-6 flex gap-2">
          <input
            v-model="newEgreso"
            type="text"
            required
            placeholder="Ej. Arriendo, Servicios, Transporte"
            class="h-10 flex-1 rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
          />
          <BaseButton type="submit" icon="plus" :loading="savingEgreso">Agregar</BaseButton>
        </form>

        <div v-if="loading" class="space-y-2 animate-pulse">
          <div v-for="n in 3" :key="n" class="h-10 rounded-lg bg-slate-100 dark:bg-slate-800" />
        </div>

        <div v-else-if="egresos.length" class="divide-y divide-slate-100 dark:divide-slate-800/60 max-h-80 overflow-y-auto pr-1">
          <div v-for="cat in egresos" :key="cat.id" class="flex items-center justify-between py-3">
            <span class="text-sm font-medium capitalize text-slate-700 dark:text-slate-200">{{ cat.nombre }}</span>
            <BaseButton
              variant="ghost"
              size="sm"
              icon="trash"
              @click="removeCategoria(cat)"
            >
              Eliminar
            </BaseButton>
          </div>
        </div>
        <EmptyState
          v-else
          icon="trend-down"
          title="Sin categorías"
          description="Crea categorías para clasificar tus gastos operativos."
        />
      </BaseCard>

      <!-- CATEGORIAS DE INVENTARIO -->
      <BaseCard title="Categorías de Inventario" subtitle="Repuestos, accesorios, herramientas, etc.">
        <form @submit.prevent="addCategoriaInventario" class="mb-6 flex gap-2">
          <input
            v-model="newCategoriaInventario"
            type="text"
            required
            placeholder="Ej. Pantallas, Baterías, Cargadores"
            class="h-10 flex-1 rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
          />
          <BaseButton type="submit" icon="plus" :loading="savingCategoriaInventario">Agregar</BaseButton>
        </form>

        <div v-if="loading" class="space-y-2 animate-pulse">
          <div v-for="n in 3" :key="n" class="h-10 rounded-lg bg-slate-100 dark:bg-slate-800" />
        </div>

        <div v-else-if="categoriasInventario.length" class="divide-y divide-slate-100 dark:divide-slate-800/60 max-h-80 overflow-y-auto pr-1">
          <div v-for="cat in categoriasInventario" :key="cat.id" class="flex items-center justify-between py-3">
            <span class="text-sm font-medium capitalize text-slate-700 dark:text-slate-200">{{ cat.nombre }}</span>
          </div>
        </div>
        <EmptyState
          v-else
          icon="repuesto"
          title="Sin categorías"
          description="Crea categorías para clasificar tus productos de inventario."
        />
      </BaseCard>
    </div>

    <!-- PREFERENCIAS LOCALES -->
    <div class="grid gap-6 md:grid-cols-3">
      <BaseCard title="Conexión API" subtitle="Configuración de backend.">
        <div class="space-y-3">
          <div>
            <p class="text-xs font-medium text-slate-500">Base URL</p>
            <p class="mt-1 break-all font-mono text-xs text-slate-950 dark:text-white">{{ apiUrl }}</p>
          </div>
          <div>
            <p class="text-xs font-medium text-slate-500">Variable Netlify</p>
            <p class="mt-1 font-mono text-xs text-slate-950 dark:text-white">VITE_API_URL</p>
          </div>
        </div>
      </BaseCard>

      <BaseCard title="Apariencia" subtitle="Contraste de pantalla.">
        <div class="flex flex-col gap-3 justify-between h-full">
          <p class="text-xs text-slate-500">Cambia el contraste del panel administrativo según tus preferencias.</p>
          <BaseButton variant="secondary" icon="moon" class="w-full" @click="ui.toggleTheme">
            {{ ui.darkMode ? 'Usar claro' : 'Usar oscuro' }}
          </BaseButton>
        </div>
      </BaseCard>

      <BaseCard title="Sesión" subtitle="Almacenamiento de token.">
        <div class="flex flex-col gap-3 justify-between h-full">
          <p class="text-xs text-slate-500">Limpia el JWT local y desconecta tu sesión de forma segura.</p>
          <BaseButton variant="danger" icon="logout" class="w-full" @click="auth.logout()">
            Cerrar sesión
          </BaseButton>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'
import EmptyState from '../components/EmptyState.vue'
import { API_BASE_URL } from '../api/http'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'
import { categoriasApi } from '../api/categoriasApi'
import { inventarioApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'

const apiUrl = API_BASE_URL
const auth = useAuthStore()
const ui = useUiStore()

const { loading, run } = useApiState()

const ingresos = ref([])
const egresos = ref([])
const categoriasInventario = ref([])

const newIngreso = ref('')
const newEgreso = ref('')
const newCategoriaInventario = ref('')
const savingIngreso = ref(false)
const savingEgreso = ref(false)
const savingCategoriaInventario = ref(false)

async function loadCategorias() {
  const [ingResponse, egrResponse, invResponse] = await Promise.all([
    run(() => categoriasApi.list('ingreso')),
    run(() => categoriasApi.list('egreso')),
    run(() => inventarioApi.listCategorias())
  ])
  ingresos.value = ingResponse.data
  egresos.value = egrResponse.data
  categoriasInventario.value = invResponse.data
}

async function addCategoria(tipo) {
  const nombre = tipo === 'ingreso' ? newIngreso.value : newEgreso.value
  if (!nombre.trim()) return

  if (tipo === 'ingreso') savingIngreso.value = true
  else savingEgreso.value = true

  try {
    await run(() => categoriasApi.create({ nombre, tipo }), 'Categoría guardada')
    if (tipo === 'ingreso') newIngreso.value = ''
    else newEgreso.value = ''
    await loadCategorias()
  } finally {
    if (tipo === 'ingreso') savingIngreso.value = false
    else savingEgreso.value = false
  }
}

async function addCategoriaInventario() {
  const nombre = newCategoriaInventario.value
  if (!nombre.trim()) return

  savingCategoriaInventario.value = true
  try {
    await run(() => inventarioApi.createCategoria({ nombre }), 'Categoría de inventario guardada')
    newCategoriaInventario.value = ''
    await loadCategorias()
  } finally {
    savingCategoriaInventario.value = false
  }
}

async function removeCategoria(cat) {
  const confirmed = await ui.confirm({
    title: `Eliminar categoría "${cat.nombre}"`,
    message: 'Se eliminará la categoría para nuevos registros.'
  })
  if (!confirmed) return

  await run(() => categoriasApi.remove(cat.id), 'Categoría eliminada')
  await loadCategorias()
}

onMounted(async () => {
  try {
    await loadCategorias()
  } catch {
    // handled by useApiState
  }
})
</script>
