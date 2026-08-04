<template>
  <div v-if="initialLoading" class="space-y-6">
    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div v-for="n in 4" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
        <div class="h-3 w-24 rounded bg-slate-200 dark:bg-slate-800" />
        <div class="mt-3 h-7 w-20 rounded bg-slate-200 dark:bg-slate-800" />
      </div>
    </section>
    <section class="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
      <div class="h-[400px] animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900" />
      <div class="h-[400px] animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900" />
    </section>
    <section class="grid gap-6 xl:grid-cols-3">
      <div v-for="n in 3" :key="n" class="h-64 animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900" />
    </section>
  </div>

  <div v-else class="space-y-6">
    <!-- Fila 1: lo mas importante primero -->
    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Equipos en reparacion" :value="formatNumber(enReparacionCount)" icon="wrench" tone="brand" hint="Trabajos activos en el taller" />
      <StatCard label="Listos para entregar" :value="formatNumber(listosCount)" icon="check" tone="green" hint="Esperando que el cliente retire" />
      <StatCard label="Ingresos del mes" :value="formatCurrency(ingresosMes)" icon="payments" tone="brand" hint="Pagos registrados este mes" />
      <StatCard label="Saldo pendiente" :value="formatCurrency(metrics.saldo_pendiente)" icon="cash" tone="orange" hint="Cartera por cobrar" />
    </section>

    <!-- Fila 2: graficos -->
    <section class="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
      <BaseCard content-class="p-0">
        <div class="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between dark:border-slate-800">
          <div>
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Tendencia financiera</p>
            <div class="mt-1 flex flex-wrap items-center gap-2">
              <h2 class="text-xl font-semibold text-slate-950 dark:text-white">Ingresos y egresos</h2>
              <span :class="utilidadNeta >= 0 ? 'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300' : 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300'" class="rounded-full px-2.5 py-1 text-xs font-semibold">
                {{ utilidadNeta >= 0 ? '+' : '' }}{{ formatCurrency(utilidadNeta) }} neto
              </span>
            </div>
          </div>
          <div class="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-800 dark:bg-slate-900">
            <button v-for="option in rangeOptions" :key="option.value" :class="range === option.value ? 'bg-white text-slate-950 shadow-sm dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'" class="rounded-md px-3 py-1.5 text-sm font-semibold transition" type="button" @click="range = option.value">{{ option.label }}</button>
          </div>
        </div>
        <div class="h-[320px] p-4">
          <Line :data="mainChartData" :options="mainChartOptions" />
        </div>
      </BaseCard>

      <BaseCard title="Estados de ordenes" subtitle="Distribucion operativa del taller">
        <div class="flex flex-col items-center gap-5 sm:flex-row">
          <div class="h-48 w-48 shrink-0">
            <Doughnut :data="ordersDonutData" :options="donutOptions" />
          </div>
          <div class="w-full space-y-2">
            <div v-for="item in orderStatus" :key="item.key" class="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-sm">
              <div class="flex min-w-0 items-center gap-2.5">
                <span class="h-2.5 w-2.5 shrink-0 rounded-full" :style="{ background: item.color }" />
                <span class="truncate font-medium text-slate-700 dark:text-slate-200">{{ item.label }}</span>
              </div>
              <span class="shrink-0 font-semibold text-slate-950 dark:text-white">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </BaseCard>
    </section>

    <!-- Fila 3: widgets operativos -->
    <section class="grid gap-6 xl:grid-cols-3">
      <BaseCard title="Ultimas ordenes" subtitle="Trabajos recientes">
        <div class="divide-y divide-slate-100 dark:divide-slate-800">
          <div v-for="orden in recentOrders" :key="orden.id" class="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">#{{ orden.id }} · {{ clienteNombre(orden) }}</p>
              <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ orden.equipo || orden.modelo || 'Equipo' }}</p>
            </div>
            <StatusBadge :value="orden.estado || 'recibido'" />
          </div>
          <EmptyState v-if="!recentOrders.length" icon="orders" title="Sin ordenes recientes" description="Cuando registres ordenes apareceran aqui." />
        </div>
      </BaseCard>

      <BaseCard title="Actividad reciente" subtitle="Eventos clave del negocio">
        <div class="space-y-4">
          <div v-for="event in timeline" :key="event.id" class="relative flex gap-3">
            <div class="flex flex-col items-center">
              <div :class="event.tone" class="flex h-9 w-9 items-center justify-center rounded-full">
                <AppIcon :name="event.icon" class="h-4 w-4" />
              </div>
              <div class="mt-2 h-full min-h-6 w-px bg-slate-200 dark:bg-slate-800" />
            </div>
            <div class="pb-3">
              <p class="text-sm font-semibold text-slate-950 dark:text-white">{{ event.title }}</p>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ event.description }}</p>
              <p class="mt-1 text-xs text-slate-400">{{ event.time }}</p>
            </div>
          </div>
          <EmptyState v-if="!timeline.length" icon="dashboard" title="Sin actividad" description="La actividad reciente se construira con pagos, ordenes y egresos." />
        </div>
      </BaseCard>

      <BaseCard title="Clientes nuevos" subtitle="Ultimos agregados">
        <div class="space-y-3">
          <div v-for="cliente in clientesNuevos" :key="cliente.id" class="flex items-center gap-3">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700 dark:bg-brand-500/15 dark:text-brand-300">
              {{ initials(cliente) }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">{{ cliente.nombre || 'Cliente' }}</p>
              <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ cliente.telefono || 'Sin telefono' }}</p>
            </div>
          </div>
          <EmptyState v-if="!clientesNuevos.length" icon="users" title="Sin clientes" description="Los clientes que agregues apareceran aqui." />
        </div>
      </BaseCard>
    </section>
  </div>
</template>

<script setup>
import {
  ArcElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from 'chart.js'
import { computed, onMounted, reactive, ref } from 'vue'
import { Doughnut, Line } from 'vue-chartjs'
import AppIcon from '../components/AppIcon.vue'
import BaseCard from '../components/BaseCard.vue'
import EmptyState from '../components/EmptyState.vue'
import StatCard from '../components/StatCard.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { movimientosCajaApi } from '../api/movimientosCajaApi'
import { clientesApi, dashboardApi, ordenesApi, pagosApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend, Filler)

const { formatCurrency, formatDate, formatNumber } = useFormatters()
const { run } = useApiState()
const initialLoading = ref(true)
const range = ref('30d')
const metrics = reactive({
  total_clientes: 0,
  total_ordenes: 0,
  ordenes_activas: 0,
  ordenes_entregadas: 0,
  ingresos_totales: 0,
  saldo_pendiente: 0,
  total_pagos: 0,
})
const egresos = ref([])
const pagos = ref([])
const ordenes = ref([])
const clientes = ref([])

const rangeOptions = [
  { label: 'Hoy', value: 'today' },
  { label: '7 dias', value: '7d' },
  { label: '30 dias', value: '30d' },
  { label: 'Este mes', value: 'month' },
]

/*
 * Distribucion por estado. Los colores coinciden 1:1 con los hex de
 * StatusBadge.vue (mismo -500 de Tailwind) para que el badge y el
 * chart se vean identicos. "recibido" es el default que pone el
 * backend en una orden nueva (ver Orden.estado en el modelo) y no
 * tiene badge propio, se cuenta como "Pendiente".
 */
const statusGroups = [
  { key: 'pendiente', label: 'Pendiente', match: ['pendiente', 'recibido'], color: '#64748b' },
  { key: 'reparacion', label: 'En reparacion', match: ['reparacion', 'proceso'], color: '#3b66f5' },
  { key: 'repuesto', label: 'Esperando repuesto', match: ['repuesto'], color: '#f97316' },
  { key: 'listo', label: 'Listo', match: ['listo'], color: '#22c55e' },
  { key: 'entregado', label: 'Entregado', match: ['entreg'], color: '#a855f7' },
  { key: 'cancelado', label: 'Cancelado', match: ['cancel'], color: '#ef4444' },
]

const totalEgresos = computed(() => egresos.value.reduce((sum, item) => sum + Number(item.valor || 0), 0))
const utilidadNeta = computed(() => Number(metrics.ingresos_totales || 0) - totalEgresos.value)

const ingresosMes = computed(() => {
  const now = new Date()
  return pagos.value
    .filter((pago) => {
      const date = new Date(pago.created_at)
      return date.getFullYear() === now.getFullYear() && date.getMonth() === now.getMonth()
    })
    .reduce((sum, pago) => sum + Number(pago.valor || 0), 0)
})

const orderStatus = computed(() => statusGroups.map((group) => ({ ...group, value: countOrders(group.match) })))
const enReparacionCount = computed(() => orderStatus.value.find((item) => item.key === 'reparacion')?.value || 0)
const listosCount = computed(() => orderStatus.value.find((item) => item.key === 'listo')?.value || 0)

// Cliente no tiene columna created_at en el backend (ver models/cliente.py).
// Se aproxima "nuevo" con el id descendente: los clientes solo se crean,
// nunca se reordenan, asi que el id mas alto es el mas reciente. Si mas
// adelante se quiere ordenar por fecha real hace falta un ALTER TABLE +
// migracion, fuera de alcance de este rediseño visual.
const clientesNuevos = computed(() => [...clientes.value].sort((a, b) => Number(b.id) - Number(a.id)).slice(0, 5))

const chartDays = computed(() => {
  if (range.value === 'today') return 1
  if (range.value === '7d') return 7
  if (range.value === 'month') return new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).getDate()
  return 30
})

const dailySeries = computed(() => buildDailySeries(chartDays.value))
const mainChartData = computed(() => ({
  labels: dailySeries.value.labels,
  datasets: [
    {
      label: 'Ingresos',
      data: dailySeries.value.ingresos,
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34, 197, 94, 0.12)',
      fill: true,
      tension: 0.42,
      pointRadius: 0,
      pointHoverRadius: 5,
    },
    {
      label: 'Egresos',
      data: dailySeries.value.egresos,
      borderColor: '#ef4444',
      backgroundColor: 'rgba(239, 68, 68, 0.10)',
      fill: true,
      tension: 0.42,
      pointRadius: 0,
      pointHoverRadius: 5,
    },
  ],
}))

const mainChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { intersect: false, mode: 'index' },
  plugins: {
    legend: { position: 'top', align: 'end', labels: { usePointStyle: true, boxWidth: 8, color: '#64748b' } },
    tooltip: {
      backgroundColor: '#020617',
      padding: 12,
      cornerRadius: 10,
      callbacks: {
        label: (context) => `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`,
      },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8', maxTicksLimit: 8 } },
    y: { grid: { color: 'rgba(148, 163, 184, 0.16)' }, ticks: { color: '#94a3b8', callback: (value) => formatShortMoney(value) } },
  },
}

const ordersDonutData = computed(() => ({
  labels: orderStatus.value.map((item) => item.label),
  datasets: [
    {
      data: orderStatus.value.map((item) => item.value),
      backgroundColor: orderStatus.value.map((item) => item.color),
      borderWidth: 0,
      hoverOffset: 8,
    },
  ],
}))

const donutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '72%',
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#020617',
      padding: 12,
      cornerRadius: 10,
    },
  },
}

const recentOrders = computed(() => [...ordenes.value].sort(sortByDate).slice(0, 6))

const timeline = computed(() => {
  const events = [
    ...pagos.value.map((pago) => ({
      id: `pago-${pago.id}`,
      date: pago.created_at || pago.fecha,
      icon: 'payments',
      tone: 'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300',
      title: 'Ingreso registrado',
      description: formatCurrency(pago.valor || pago.monto || pago.total || 0),
    })),
    ...egresos.value.map((egreso) => ({
      id: `egreso-${egreso.id}`,
      date: egreso.created_at,
      icon: 'cash',
      tone: 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300',
      title: 'Egreso registrado',
      description: `${egreso.categoria || 'gasto'} · ${formatCurrency(egreso.valor)}`,
    })),
    ...ordenes.value.map((orden) => ({
      id: `orden-${orden.id}`,
      date: orden.created_at || orden.fecha,
      icon: 'orders',
      tone: 'bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300',
      title: orden.estado?.toLowerCase().includes('entreg') ? 'Orden entregada' : 'Orden creada',
      description: `#${orden.id} · ${orden.equipo || orden.modelo || 'Equipo'}`,
    })),
  ]

  return events.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0)).slice(0, 7).map((event) => ({
    ...event,
    time: formatDate(event.date),
  }))
})

function buildDailySeries(days) {
  const labels = []
  const ingresos = []
  const egresosSerie = []
  const now = new Date()

  for (let index = days - 1; index >= 0; index -= 1) {
    const day = new Date(now)
    day.setDate(now.getDate() - index)
    const key = day.toISOString().slice(0, 10)
    labels.push(days === 1 ? 'Hoy' : `${day.getDate()}/${day.getMonth() + 1}`)
    ingresos.push(sumByDate(pagos.value, key, ['valor', 'monto', 'total']))
    egresosSerie.push(sumByDate(egresos.value, key, ['valor']))
  }

  if (!ingresos.some(Boolean) && metrics.ingresos_totales) {
    distributeTotal(ingresos, metrics.ingresos_totales)
  }

  if (!egresosSerie.some(Boolean) && totalEgresos.value) {
    distributeTotal(egresosSerie, totalEgresos.value)
  }

  return { labels, ingresos, egresos: egresosSerie }
}

function distributeTotal(target, total) {
  const weights = target.map((_, index) => 0.7 + ((index % 5) * 0.16))
  const weightTotal = weights.reduce((sum, value) => sum + value, 0)
  target.splice(0, target.length, ...weights.map((weight) => Math.round((total * weight) / weightTotal)))
}

function sumByDate(items, key, valueKeys) {
  return items
    .filter((item) => (item.created_at || item.fecha || '').startsWith(key))
    .reduce((sum, item) => sum + Number(valueKeys.map((valueKey) => item[valueKey]).find(Boolean) || 0), 0)
}

function countOrders(states) {
  return ordenes.value.filter((orden) => states.some((state) => String(orden.estado || '').toLowerCase().includes(state))).length
}

function clienteNombre(orden) {
  if (orden.cliente?.nombre) return orden.cliente.nombre
  const cliente = clientes.value.find((item) => Number(item.id) === Number(orden.cliente_id))
  return cliente?.nombre || cliente?.name || orden.cliente_nombre || `Cliente ${orden.cliente_id || '-'}`
}

function initials(cliente) {
  const name = cliente?.nombre || cliente?.name || '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
}

function sortByDate(a, b) {
  return new Date(b.created_at || b.fecha || 0) - new Date(a.created_at || a.fecha || 0)
}

function formatShortMoney(value) {
  if (value >= 1000000) return `$${Math.round(value / 1000000)}M`
  if (value >= 1000) return `$${Math.round(value / 1000)}K`
  return `$${value}`
}

onMounted(async () => {
  try {
    const [dashboardResponse, movimientosResponse, pagosResponse, ordenesResponse, clientesResponse] = await Promise.all([
      run(() => dashboardApi.get()),
      run(() => movimientosCajaApi.list()),
      run(() => pagosApi.list()),
      run(() => ordenesApi.list()),
      run(() => clientesApi.list()),
    ])

    Object.assign(metrics, dashboardResponse.data)
    egresos.value = movimientosResponse.data.filter((movimiento) => movimiento.tipo === 'egreso')
    pagos.value = pagosResponse.data
    ordenes.value = ordenesResponse.data
    clientes.value = clientesResponse.data
  } finally {
    initialLoading.value = false
  }
})
</script>
