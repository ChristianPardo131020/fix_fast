<template>
  <div class="space-y-6">
    <PageHeader title="Otros ingresos">
      <template #eyebrow>
        <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300">Ingresos</span>
        <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:bg-slate-800 dark:text-slate-300">Sin factura</span>
      </template>
      Ventas de mostrador y otros ingresos que no requieren factura ni datos del cliente: pilas, accesorios, servicios rapidos.
      Los pagos de ordenes con factura se registran desde <RouterLink :to="{ name: 'pagos' }" class="font-medium text-brand-600 hover:underline dark:text-brand-400">Pagos</RouterLink>.
      <template #actions>
        <div class="hidden sm:block">
          <BaseButton icon="plus" @click="modalOpen = true">Nuevo ingreso</BaseButton>
        </div>
      </template>
    </PageHeader>

    <FabButton label="Nuevo ingreso" @click="modalOpen = true" />

    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Total ingresos" :value="formatCurrency(summary.total)" icon="trend-up" tone="green" hint="Ingresos sin factura filtrados" />
      <StatCard label="Ingreso promedio" :value="formatCurrency(summary.promedio)" icon="dashboard" tone="slate" hint="Promedio por movimiento" />
      <StatCard label="Mayor ingreso" :value="formatCurrency(summary.mayor)" icon="cash" tone="brand" hint="Venta mas alta filtrada" />
      <StatCard label="Movimientos" :value="formatNumber(filteredMovimientos.length)" icon="orders" tone="sky" hint="Registros de ingreso" />
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <BaseCard title="Ingresos por metodo" subtitle="Distribucion de entradas segun la forma de pago">
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
        <EmptyState v-if="!methodBars.length" icon="cash" title="Sin ingresos" description="Registra ventas para visualizar los ingresos por metodo de pago." />
      </BaseCard>

      <BaseCard title="Ingresos por categoria" subtitle="Que se esta vendiendo mas, de un vistazo">
        <div v-if="categoryBars.length" class="space-y-4">
          <div v-for="item in categoryBars" :key="item.categoria">
            <div class="mb-2 flex items-center justify-between gap-4 text-sm">
              <span class="font-medium capitalize text-slate-700 dark:text-slate-200">{{ item.categoria.replace('_', ' ') }}</span>
              <span class="text-slate-500 dark:text-slate-400">{{ formatCurrency(item.total) }}</span>
            </div>
            <div class="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div class="h-full rounded-full bg-green-500" :style="{ width: `${item.percent}%` }" />
            </div>
          </div>
        </div>
        <EmptyState v-else icon="cash" title="Sin ingresos" description="Los ingresos por categoria apareceran cuando registres ventas." />
      </BaseCard>
    </div>

    <BaseCard title="Otros ingresos" subtitle="Ventas y entradas sin factura, con trazabilidad" content-class="p-4">
      <div class="mb-4 grid gap-3 lg:grid-cols-[1fr_190px_170px]">
        <label class="relative block">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" />
          <input v-model="filters.search" class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950" placeholder="Buscar descripcion, metodo o categoria" />
        </label>
        <BaseInput v-model="filters.categoria" type="select">
          <option value="">Todas las categorias</option>
          <option v-for="categoria in categorias" :key="categoria" :value="categoria">{{ categoria.replace('_', ' ') }}</option>
        </BaseInput>
        <BaseInput v-model="filters.fecha" type="date" />
      </div>

      <FinanceMovementsTable :rows="filteredMovimientos" :loading="loading" @delete="removeMovimiento" />
    </BaseCard>

    <MovimientoCajaModal v-model="modalOpen" tipo="ingreso" :loading="saving" @save="saveMovimiento" />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import EmptyState from '../components/EmptyState.vue'
import FabButton from '../components/FabButton.vue'
import FinanceMovementsTable from '../components/FinanceMovementsTable.vue'
import MovimientoCajaModal from '../components/MovimientoCajaModal.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import { movimientosCajaApi } from '../api/movimientosCajaApi'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'
import { useUiStore } from '../stores/ui'

const { formatCurrency, formatNumber } = useFormatters()
const { loading, run } = useApiState()
const ui = useUiStore()

const movimientos = ref([])
const modalOpen = ref(false)
const saving = ref(false)
const categorias = ['venta', 'accesorio', 'pila', 'servicio_rapido', 'otros']
const filters = reactive({ search: '', categoria: '', fecha: '' })

const filteredMovimientos = computed(() => {
  const term = filters.search.toLowerCase().trim()

  return movimientos.value.filter((movimiento) => {
    const matchesSearch = !term || JSON.stringify(movimiento).toLowerCase().includes(term)
    const matchesTipo = movimiento.tipo === 'ingreso'
    const matchesCategoria = !filters.categoria || movimiento.categoria === filters.categoria
    const matchesFecha = !filters.fecha || movimiento.created_at?.startsWith(filters.fecha)

    return matchesSearch && matchesTipo && matchesCategoria && matchesFecha
  })
})

const summary = computed(() => {
  const valores = filteredMovimientos.value.map((item) => Number(item.valor || 0))
  const total = valores.reduce((sum, valor) => sum + valor, 0)

  return {
    total,
    promedio: valores.length ? total / valores.length : 0,
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

const categoryBars = computed(() => {
  const totals = filteredMovimientos.value.reduce((acc, item) => {
    const categoria = item.categoria || 'otros'
    acc[categoria] = (acc[categoria] || 0) + Number(item.valor || 0)
    return acc
  }, {})

  const max = Math.max(...Object.values(totals), 1)

  return Object.entries(totals)
    .map(([categoria, total]) => ({ categoria, total, percent: Math.max((total / max) * 100, 6) }))
    .sort((a, b) => b.total - a.total)
})

async function loadMovimientos() {
  const response = await run(() => movimientosCajaApi.list())
  movimientos.value = response.data.filter((movimiento) => movimiento.tipo === 'ingreso')
}

async function saveMovimiento(payload) {
  if (!payload.valor || payload.valor <= 0) {
    return
  }

  saving.value = true

  try {
    await run(() => movimientosCajaApi.create(payload), 'Ingreso registrado')
    modalOpen.value = false
    await loadMovimientos()
  } finally {
    saving.value = false
  }
}

async function removeMovimiento(movimiento) {
  const confirmed = await ui.confirm({
    title: `Eliminar ingreso de ${formatCurrency(movimiento.valor)}`,
    message: 'Esta accion no se puede deshacer.',
  })
  if (!confirmed) return
  await run(() => movimientosCajaApi.remove(movimiento.id), 'Ingreso eliminado')
  await loadMovimientos()
}

onMounted(loadMovimientos)
</script>
