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
        <BaseButton icon="plus" @click="modalOpen = true">Nuevo egreso</BaseButton>
      </template>
    </PageHeader>

    <FilterBar>
      <BaseSelect v-model="selectedMonth" variant="card">
        <option :value="null">Todos los meses</option>
        <option v-for="(mes, index) in meses" :key="mes" :value="index + 1">{{ mes }}</option>
      </BaseSelect>
      <BaseSelect v-if="selectedMonth !== null" v-model="selectedDay" variant="card">
        <option :value="null">Todos los días</option>
        <option v-for="d in daysInSelectedMonth" :key="d" :value="d">{{ d }}</option>
      </BaseSelect>
      <BaseSelect v-model="selectedYear" variant="card">
        <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
      </BaseSelect>
      <div class="flex flex-col gap-3 sm:ml-auto sm:flex-row">
        <SearchField v-model="filters.search" class="sm:w-72" placeholder="Buscar descripción, método o categoría" />
        <BaseSelect v-model="filters.categoria" variant="card" class="sm:w-48">
          <option value="">Todas las categorías</option>
          <option v-for="cat in categoriasList" :key="cat" :value="cat">{{ cat }}</option>
        </BaseSelect>
      </div>
    </FilterBar>

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
      <FinanceMovementsTable :rows="filteredMovimientos" :loading="loading" @delete="removeMovimiento" />
    </BaseCard>

    <MovimientoCajaModal v-model="modalOpen" :loading="saving" @save="saveMovimiento" />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseSelect from '../components/BaseSelect.vue'
import EmptyState from '../components/EmptyState.vue'
import FilterBar from '../components/FilterBar.vue'
import FinanceMovementsTable from '../components/FinanceMovementsTable.vue'
import MovimientoCajaModal from '../components/MovimientoCajaModal.vue'
import PageHeader from '../components/PageHeader.vue'
import SearchField from '../components/SearchField.vue'
import StatCard from '../components/StatCard.vue'
import { movimientosCajaApi } from '../api/movimientosCajaApi'
import { categoriasApi } from '../api/categoriasApi'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'
import { useUiStore } from '../stores/ui'
import { normalizarTexto } from '../utils/texto'

const { formatCurrency, formatNumber, parseUTC } = useFormatters()
const { loading, run } = useApiState()
const ui = useUiStore()
const route = useRoute()
const router = useRouter()

const movimientos = ref([])
const categoriasDinamicas = ref([])
const modalOpen = ref(false)
const saving = ref(false)

const categoriasList = computed(() => {
  const base = categoriasDinamicas.value.length
    ? categoriasDinamicas.value.map(c => c.nombre)
    : ['arriendo', 'empleado', 'servicios', 'herramientas', 'transporte', 'compra', 'prestamo', 'otros']
  // Incluir la categoría generada por compras de inventario
  if (!base.includes('compra_inventario')) base.push('compra_inventario')
  return base
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
    const d = parseUTC(m.created_at)
    if (d) years.add(d.getFullYear())
  })
  return [...years].sort((a, b) => b - a)
})

const daysInSelectedMonth = computed(() => {
  if (!selectedMonth.value) return 0
  return new Date(selectedYear.value, selectedMonth.value, 0).getDate()
})

const filteredMovimientos = computed(() => {
  const term = normalizarTexto(filters.search)

  return movimientos.value.filter((movimiento) => {
    const matchesSearch = !term || (
      normalizarTexto(movimiento.descripcion).includes(term)
      || normalizarTexto(movimiento.metodo_pago).includes(term)
      || normalizarTexto(movimiento.categoria).includes(term)
    )
    const matchesTipo = movimiento.tipo === 'egreso'
    const matchesCategoria = !filters.categoria || movimiento.categoria === filters.categoria

    const fecha = parseUTC(movimiento.created_at)
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
  loading.value = true
  try {
    const [movRes, catRes] = await Promise.allSettled([
      movimientosCajaApi.list(),
      categoriasApi.list('egreso'),
    ])
    if (movRes.status === 'fulfilled') {
      movimientos.value = movRes.value.data.filter((m) => m.tipo === 'egreso')
    } else {
      console.error('Error al cargar egresos:', movRes.reason)
      ui.toast('No se pudieron cargar los egresos', 'error')
    }
    if (catRes.status === 'fulfilled') categoriasDinamicas.value = catRes.value.data
  } finally {
    loading.value = false
  }
}

async function saveMovimiento(payload) {
  if (!payload.valor || payload.valor <= 0) {
    ui.toast('El valor debe ser mayor a 0', 'error')
    return
  }

  saving.value = true

  try {
    await run(() => movimientosCajaApi.create({ ...payload, tipo: 'egreso' }), 'Egreso registrado')
    modalOpen.value = false
    await loadMovimientos()
  } catch {
    // run() ya mostró el toast de error — el modal queda abierto para reintentar
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
