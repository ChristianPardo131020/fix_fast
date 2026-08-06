<template>
  <div class="space-y-6">
    <PageHeader title="Resumen general" subtitle="Esto es lo que esta pasando en tu taller.">
      <template #actions>
        <div class="flex items-center gap-2">
          <select
            v-model="selectedMonth"
            class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
          >
            <option :value="null">Todos los meses</option>
            <option v-for="(mes, index) in meses" :key="mes" :value="index">{{ mes }}</option>
          </select>
          <select
            v-model="selectedYear"
            class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
          >
            <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
      </template>
    </PageHeader>

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
      <StatCard label="Equipos en reparacion" :value="formatNumber(enReparacionCount)" icon="wrench" tone="brand" hint="Trabajos activos en el taller ahora" />
      <StatCard label="Listos para entregar" :value="formatNumber(listosCount)" icon="check" tone="green" hint="Esperando que el cliente retire" />
      <StatCard label="Ingresos del periodo" :value="formatCurrency(ingresosPeriodo)" icon="payments" tone="brand" :hint="`Pagos y otros ingresos · ${periodLabel}`" />
      <StatCard label="Saldo pendiente" :value="formatCurrency(saldoPendiente)" icon="cash" tone="orange" hint="Cartera por cobrar, todas las ordenes" />
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
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {{ selectedMonth === null ? 'Por mes' : 'Por dia' }} · {{ periodLabel }}
          </span>
        </div>
        <div class="h-[320px] p-4">
          <Line :data="mainChartData" :options="mainChartOptions" />
        </div>
      </BaseCard>

      <BaseCard title="Estados de ordenes" subtitle="Distribucion operativa del taller">
        <div class="flex flex-col items-center gap-5 sm:flex-row">
          <div class="relative h-48 w-48 shrink-0">
            <Doughnut :data="ordersDonutData" :options="donutOptions" />
            <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <span class="text-2xl font-semibold text-slate-950 dark:text-white">{{ formatNumber(ordenes.length) }}</span>
              <span class="text-xs text-slate-400">Total</span>
            </div>
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
      <BaseCard title="Ultimas ordenes" subtitle="Trabajos recientes del periodo">
        <div class="divide-y divide-slate-100 dark:divide-slate-800">
          <div v-for="orden in recentOrders" :key="orden.id" class="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-slate-950 dark:text-white"><span class="font-mono text-slate-400">ORD-{{ orden.id }}</span> · {{ clienteNombre(orden) }}</p>
              <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ orden.equipo || orden.modelo || 'Equipo' }}</p>
            </div>
            <StatusBadge :value="orden.estado || 'recibido'" />
          </div>
          <EmptyState v-if="!recentOrders.length" icon="orders" title="Sin ordenes en este periodo" description="Prueba con otro mes o año para ver ordenes." />
        </div>
      </BaseCard>

      <BaseCard title="Actividad reciente" subtitle="Eventos clave del periodo">
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
          <EmptyState v-if="!timeline.length" icon="dashboard" title="Sin actividad en este periodo" description="Prueba con otro mes o año para ver actividad." />
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
import { computed, onMounted, ref } from 'vue'
import { Doughnut, Line } from 'vue-chartjs'
import AppIcon from '../components/AppIcon.vue'
import BaseCard from '../components/BaseCard.vue'
import EmptyState from '../components/EmptyState.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { movimientosCajaApi } from '../api/movimientosCajaApi'
import { clientesApi, ordenesApi, pagosApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend, Filler)

const { formatCurrency, formatDate, formatNumber } = useFormatters()
const { run } = useApiState()
const initialLoading = ref(true)
const egresos = ref([])
const otrosIngresos = ref([])
const pagos = ref([])
const ordenes = ref([])
const clientes = ref([])

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const mesesCortos = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

// Filtro de periodo del dashboard completo. selectedMonth en null significa
// "todos los meses" (agrega todo selectedYear); por defecto arranca en el
// mes/año actual, que es el recorte que la mayoria va a querer ver primero.
const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth())

// El selector de año se arma con los años que realmente tienen datos (mas
// el año actual, para que nunca quede vacio en una instalacion nueva) en
// vez de una lista fija que podria no cubrir historico real importado.
const availableYears = computed(() => {
  const years = new Set([now.getFullYear()])
  const dates = [
    ...ordenes.value.map((orden) => orden.fecha_ingreso || orden.created_at),
    ...pagos.value.map((pago) => pago.created_at || pago.fecha),
    ...egresos.value.map((item) => item.created_at),
    ...otrosIngresos.value.map((item) => item.created_at),
  ]
  dates.filter(Boolean).forEach((date) => years.add(Number(String(date).slice(0, 4))))
  return [...years].sort((a, b) => b - a)
})

// Prefijo ISO para filtrar por coincidencia de texto: "2026" para todo el
// año, o "2026-08" para un mes especifico. Mismo truco que ya usaba
// sumByPrefix mas abajo, evita crear objetos Date (y sus problemas de
// timezone) solo para comparar año/mes.
const periodKey = computed(() => {
  const year = String(selectedYear.value)
  if (selectedMonth.value === null) return year
  return `${year}-${String(selectedMonth.value + 1).padStart(2, '0')}`
})

const periodLabel = computed(() => {
  if (selectedMonth.value === null) return `Todo ${selectedYear.value}`
  return `${meses[selectedMonth.value]} ${selectedYear.value}`
})

function matchesPeriod(dateStr) {
  return Boolean(dateStr) && String(dateStr).startsWith(periodKey.value)
}

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

// "Ordenes del periodo" (para financiero y actividad reciente) son las
// que INGRESARON en el mes/año elegido. Esto es distinto del estado
// EN VIVO del taller (ver orderStatus/enReparacionCount/listosCount mas
// abajo): un equipo que entro en julio y sigue en reparacion en agosto
// debe seguir contando como "en reparacion ahora" sin importar que mes
// mires en el dashboard, por eso esos contadores NO usan este filtro.
const ordenesPeriodo = computed(() => ordenes.value.filter((orden) => matchesPeriod(orden.fecha_ingreso || orden.created_at)))
const pagosPeriodo = computed(() => pagos.value.filter((pago) => matchesPeriod(pago.created_at || pago.fecha)))
const otrosIngresosPeriodo = computed(() => otrosIngresos.value.filter((item) => matchesPeriod(item.created_at)))
const egresosPeriodo = computed(() => egresos.value.filter((item) => matchesPeriod(item.created_at)))

const totalEgresosPeriodo = computed(() => egresosPeriodo.value.reduce((sum, item) => sum + Number(item.valor || 0), 0))

const ingresosPeriodo = computed(() => {
  const pagosSum = pagosPeriodo.value.reduce((sum, pago) => sum + Number(pago.valor || 0), 0)
  const otrosSum = otrosIngresosPeriodo.value.reduce((sum, item) => sum + Number(item.valor || 0), 0)
  return pagosSum + otrosSum
})

const utilidadNeta = computed(() => ingresosPeriodo.value - totalEgresosPeriodo.value)

// Estado EN VIVO del taller: cuenta sobre TODAS las ordenes (no solo las
// del periodo filtrado), porque "cuantos equipos tengo en reparacion
// ahora" no depende de en que mes entraron. El filtro de mes/año solo
// aplica a las metricas financieras y de actividad de arriba/abajo.
const saldoPendiente = computed(() => ordenes.value.reduce((sum, orden) => sum + Number(orden.saldo || 0), 0))

const orderStatus = computed(() => statusGroups.map((group) => ({ ...group, value: countOrders(group.match, ordenes.value) })))
const enReparacionCount = computed(() => orderStatus.value.find((item) => item.key === 'reparacion')?.value || 0)
const listosCount = computed(() => orderStatus.value.find((item) => item.key === 'listo')?.value || 0)

// Cliente no tiene columna created_at en el backend (ver models/cliente.py).
// Se aproxima "nuevo" con el id descendente: los clientes solo se crean,
// nunca se reordenan, asi que el id mas alto es el mas reciente. No se
// puede filtrar por periodo de forma honesta sin esa columna, asi que
// esta tarjeta queda fuera del filtro de mes/año a proposito.
const clientesNuevos = computed(() => [...clientes.value].sort((a, b) => Number(b.id) - Number(a.id)).slice(0, 5))

// Un punto por mes cuando se ve "todo el año" (12 puntos, agregado
// mensual); un punto por dia cuando hay un mes especifico seleccionado.
// Evita mostrar 365 puntos diarios de golpe y hace que "todos los meses"
// sea realmente una vista comparativa mes a mes.
const dailySeries = computed(() => {
  const labels = []
  const ingresosSerie = []
  const egresosSerie = []

  if (selectedMonth.value === null) {
    for (let mes = 0; mes < 12; mes += 1) {
      const key = `${selectedYear.value}-${String(mes + 1).padStart(2, '0')}`
      labels.push(mesesCortos[mes])
      ingresosSerie.push(sumByPrefix(pagos.value, key, ['valor', 'monto', 'total']) + sumByPrefix(otrosIngresos.value, key, ['valor']))
      egresosSerie.push(sumByPrefix(egresos.value, key, ['valor']))
    }
  } else {
    const daysInMonth = new Date(selectedYear.value, selectedMonth.value + 1, 0).getDate()
    for (let dia = 1; dia <= daysInMonth; dia += 1) {
      const key = `${selectedYear.value}-${String(selectedMonth.value + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`
      labels.push(String(dia))
      ingresosSerie.push(sumByPrefix(pagos.value, key, ['valor', 'monto', 'total']) + sumByPrefix(otrosIngresos.value, key, ['valor']))
      egresosSerie.push(sumByPrefix(egresos.value, key, ['valor']))
    }
  }

  return { labels, ingresos: ingresosSerie, egresos: egresosSerie }
})

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

const recentOrders = computed(() => [...ordenesPeriodo.value].sort(sortByDate).slice(0, 6))

const timeline = computed(() => {
  const events = [
    ...pagosPeriodo.value.map((pago) => ({
      id: `pago-${pago.id}`,
      date: pago.created_at || pago.fecha,
      icon: 'payments',
      tone: 'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300',
      title: 'Ingreso registrado',
      description: formatCurrency(pago.valor || pago.monto || pago.total || 0),
    })),
    ...egresosPeriodo.value.map((egreso) => ({
      id: `egreso-${egreso.id}`,
      date: egreso.created_at,
      icon: 'cash',
      tone: 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300',
      title: 'Egreso registrado',
      description: `${egreso.categoria || 'gasto'} · ${formatCurrency(egreso.valor)}`,
    })),
    ...otrosIngresosPeriodo.value.map((ingreso) => ({
      id: `ingreso-${ingreso.id}`,
      date: ingreso.created_at,
      icon: 'trend-up',
      tone: 'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300',
      title: 'Venta registrada',
      description: `${(ingreso.categoria || 'otros').replace('_', ' ')} · ${formatCurrency(ingreso.valor)}`,
    })),
    ...ordenesPeriodo.value.map((orden) => ({
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

function sumByPrefix(items, prefix, valueKeys) {
  return items
    .filter((item) => (item.created_at || item.fecha || '').startsWith(prefix))
    .reduce((sum, item) => sum + Number(valueKeys.map((valueKey) => item[valueKey]).find(Boolean) || 0), 0)
}

function countOrders(states, list) {
  return list.filter((orden) => states.some((state) => String(orden.estado || '').toLowerCase().includes(state))).length
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
    const [movimientosResponse, pagosResponse, ordenesResponse, clientesResponse] = await Promise.all([
      run(() => movimientosCajaApi.list()),
      run(() => pagosApi.list()),
      run(() => ordenesApi.list()),
      run(() => clientesApi.list()),
    ])

    egresos.value = movimientosResponse.data.filter((movimiento) => movimiento.tipo === 'egreso')
    otrosIngresos.value = movimientosResponse.data.filter((movimiento) => movimiento.tipo === 'ingreso')
    pagos.value = pagosResponse.data
    ordenes.value = ordenesResponse.data
    clientes.value = clientesResponse.data
  } finally {
    initialLoading.value = false
  }
})
</script>
