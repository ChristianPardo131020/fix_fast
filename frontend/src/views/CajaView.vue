<template>
  <div class="space-y-6">
    <PageHeader title="Egresos">
      <template #eyebrow>
        <span class="rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-rose-700 dark:bg-rose-500/15 dark:text-rose-300">Egresos</span>
        <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">Caja operativa</span>
      </template>
      Controla arriendos, empleados, servicios, compras, herramientas, transportes y otros gastos del taller. Los pagos
      de ordenes y otras ventas se registran desde <RouterLink :to="{ name: 'pagos' }" class="font-medium text-brand-600 hover:underline dark:text-brand-400">Ingresos</RouterLink>.
      <template #actions>
        <div class="flex items-center gap-2">
           <select v-model="selectedMonth" class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
             <option :value="null">Todos los meses</option>
             <option v-for="(mes, index) in meses" :key="mes" :value="index + 1">{{ mes }}</option>
           </select>
           <select v-if="selectedMonth !== null" v-model="selectedDay" class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
             <option :value="null">Todos los días</option>
             <option v-for="d in daysInSelectedMonth" :key="d" :value="d">{{ d }}</option>
           </select>
           <select v-model="selectedYear" class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
             <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
           </select>
           <BaseButton icon="plus" @click="modalOpen = true">Nuevo egreso</BaseButton>
        </div>
      </template>
    </PageHeader>

    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Total egresos" :value="formatCurrency(summary.egresos)" icon="cash" tone="rose" hint="Gastos y salidas filtradas" />
      <StatCard label="Egreso promedio" :value="formatCurrency(summary.promedio)" icon="dashboard" tone="slate" hint="Promedio por movimiento" />
      <StatCard label="Mayor egreso" :value="formatCurrency(summary.mayor)" icon="cash" tone="amber" hint="Salida mas alta filtrada" />
      <StatCard label="Movimientos" :value="formatNumber(filteredMovimientos.length)" icon="orders" tone="sky" hint="Registros de gasto" />
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <BaseCard title="Egresos por metodo" subtitle="Distribucion de salidas segun la forma de pago">
        <div class="space-y-5">
          <div v-for="item in methodBars" :key="item.label">
            <div class="mb-2 flex items-center justify-between text-sm">
              <span class="font-medium text-slate-700 dark:text-slate-200">{{ item.label }}</span>
              <span class="text-slate-500 dark:text-slate-400">{{ formatCurrency(item.value) }}</span>
            </div>
            <div class="h-4 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div class="h-full rounded-full bg-slate-950 transition-all dark:bg-white" :style="{ width: `${item.percent}%` }" />
            </div>
          </div>
        </div>
        <EmptyState v-if="!methodBars.length" icon="cash" title="Sin egresos" description="Registra gastos para visualizar la caja por metodo de pago." />
        <div class="mt-6 grid gap-3 sm:grid-cols-3">
          <div v-for="metric in miniMetrics" :key="metric.label" class="rounded-xl bg-slate-50 p-4 dark:bg-slate-800/60">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">{{ metric.label }}</p>
            <p class="mt-2 text-lg font-semibold text-slate-950 dark:text-white">{{ metric.value }}</p>
          </div>
        </div>
      </BaseCard>

      <BaseCard title="Gastos por categoria" subtitle="Ranking de egresos para decisiones rapidas">
        <div v-if="expenseCategories.length" class="space-y-4">
          <div v-for="item in expenseCategories" :key="item.categoria">
            <div class="mb-2 flex items-center justify-between gap-4 text-sm">
              <span class="font-medium capitalize text-slate-700 dark:text-slate-200">{{ item.categoria }}</span>
              <span class="text-slate-500 dark:text-slate-400">{{ formatCurrency(item.total) }}</span>
            </div>
            <div class="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div class="h-full rounded-full bg-rose-500" :style="{ width: `${item.percent}%` }" />
            </div>
          </div>
        </div>
        <EmptyState v-else icon="cash" title="Sin egresos" description="Los gastos por categoria apareceran cuando registres egresos." />
      </BaseCard>
    </div>

    <BaseCard title="Egresos de caja" subtitle="Gastos operativos y trazabilidad financiera" content-class="p-4">
      <div class="mb-4 grid gap-3 lg:grid-cols-[1fr_190px]">
        <label class="relative block">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" />
          <input v-model="filters.search" class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950" placeholder="Buscar descripción, método o categoría" />
        </label>
        <BaseInput v-model="filters.categoria" type="select">
          <option value="">Todas las categorías</option>
          <option v-for="cat in categoriasList" :key="cat" :value="cat">{{ cat }}</option>
        </BaseInput>
      </div>

      <FinanceMovementsTable :rows="filteredMovimientos" :loading="loading" @delete="removeMovimiento" />
    </BaseCard>

    <MovimientoCajaModal v-model="modalOpen" :loading="saving" @save="saveMovimiento" />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import EmptyState from '../components/EmptyState.vue'
import FinanceMovementsTable from '../components/FinanceMovementsTable.vue'
import MovimientoCajaModal from '../components/MovimientoCajaModal.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import { movimientosCajaApi } from '../api/movimientosCajaApi'
import { categoriasApi } from '../api/categoriasApi'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'
import { useUiStore } from '../stores/ui'

const { formatCurrency, formatNumber } = useFormatters()
const { loading, run } = useApiState()
const ui = useUiStore()
const route = useRoute()
const router = useRouter()

const movimientos = ref([])
const categoriasDinamicas = ref([])
const modalOpen = ref(false)
const saving = ref(false)

const categoriasList = computed(() => {
  if (categoriasDinamicas.value.length) {
    return categoriasDinamicas.value.map(c => c.nombre)
  }
  return ['arriendo', 'empleado', 'servicios', 'herramientas', 'transporte', 'compra', 'prestamo', 'otros']
})

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth() + 1)
const selectedDay = ref(now.getDate())

const filters = reactive({ search: '', categoria: '' })

const availableYears = computed(() => {
  const years = new Set([now.getFullYear()])
  movimientos.value.forEach(m => {
    if (m.created_at) {
      years.add(new Date(m.created_at).getFullYear())
    }
  })
  return [...years].sort((a, b) => b - a)
})

const daysInSelectedMonth = computed(() => {
  if (!selectedMonth.value) return 0
  return new Date(selectedYear.value, selectedMonth.value, 0).getDate()
})

const filteredMovimientos = computed(() => {
  const term = filters.search.toLowerCase().trim()

  return movimientos.value.filter((movimiento) => {
    const matchesSearch = !term || (
      movimiento.descripcion?.toLowerCase().includes(term)
      || movimiento.metodo_pago?.toLowerCase().includes(term)
      || movimiento.categoria?.toLowerCase().includes(term)
    )
    const matchesTipo = movimiento.tipo === 'egreso'
    const matchesCategoria = !filters.categoria || movimiento.categoria === filters.categoria

    const fecha = movimiento.created_at ? new Date(movimiento.created_at) : null
    if (!fecha) return false

    const matchesYear = fecha.getFullYear() === selectedYear.value
    const matchesMonth = selectedMonth.value === null || (fecha.getMonth() + 1) === selectedMonth.value
    const matchesDay = selectedDay.value === null || fecha.getDate() === selectedDay.value

    return matchesSearch && matchesTipo && matchesCategoria && matchesYear && matchesMonth && matchesDay
  })
})

const summary = computed(() => {
  const valores = filteredMovimientos.value.map((item) => Number(item.valor || 0))
  const egresos = valores.reduce((sum, valor) => sum + valor, 0)

  return {
    egresos,
    promedio: valores.length ? egresos / valores.length : 0,
    mayor: Math.max(...valores, 0),
  }
})

const methodBars = computed(() => {
  const totals = filteredMovimientos.value.reduce((acc, item) => {
    const method = item.metodo_pago || 'sin metodo'
    acc[method] = (acc[method] || 0) + Number(item.valor || 0)
    return acc
  }, {})

  const max = Math.max(...Object.values(totals), 1)

  return Object.entries(totals)
    .map(([label, value]) => ({ label, value, percent: Math.max((value / max) * 100, 6) }))
    .sort((a, b) => b.value - a.value)
})

const expenseCategories = computed(() => {
  const totals = filteredMovimientos.value
    .filter((item) => item.tipo === 'egreso')
    .reduce((acc, item) => {
      const categoria = item.categoria || 'otros'
      acc[categoria] = (acc[categoria] || 0) + Number(item.valor || 0)
      return acc
    }, {})

  const max = Math.max(...Object.values(totals), 1)

  return Object.entries(totals)
    .map(([categoria, total]) => ({ categoria, total, percent: Math.max((total / max) * 100, 6) }))
    .sort((a, b) => b.total - a.total)
})

const miniMetrics = computed(() => [
  { label: 'Movimientos', value: formatNumber(filteredMovimientos.value.length) },
  { label: 'Categorias', value: formatNumber(new Set(filteredMovimientos.value.map((item) => item.categoria)).size) },
  { label: 'Ticket promedio', value: formatCurrency(averageTicket.value) },
])

const averageTicket = computed(() => {
  if (!filteredMovimientos.value.length) return 0
  const total = filteredMovimientos.value.reduce((sum, item) => sum + Number(item.valor || 0), 0)
  return total / filteredMovimientos.value.length
})

async function loadMovimientos() {
  const [movResponse, catResponse] = await Promise.all([
    run(() => movimientosCajaApi.list()),
    run(() => categoriasApi.list('egreso'))
  ])
  movimientos.value = movResponse.data.filter((movimiento) => movimiento.tipo === 'egreso')
  categoriasDinamicas.value = catResponse.data
}

async function saveMovimiento(payload) {
  if (!payload.valor || payload.valor <= 0) {
    return
  }

  saving.value = true

  try {
    await run(() => movimientosCajaApi.create({ ...payload, tipo: 'egreso' }), 'Egreso registrado')
    modalOpen.value = false
    await loadMovimientos()
  } finally {
    saving.value = false
  }
}

async function removeMovimiento(movimiento) {
  const confirmed = await ui.confirm({
    title: `Eliminar movimiento de ${formatCurrency(movimiento.valor)}`,
    message: 'Esta accion no se puede deshacer.',
  })
  if (!confirmed) return
  await run(() => movimientosCajaApi.remove(movimiento.id), 'Movimiento eliminado')
  await loadMovimientos()
}

onMounted(async () => {
  try {
    await loadMovimientos()
  } catch {
    // noop, ya notificado por useApiState
  }
  if (route.query.crear === '1') {
    modalOpen.value = true
    const { crear, ...rest } = route.query
    router.replace({ query: rest })
  }
})
</script>
