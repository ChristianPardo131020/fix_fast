<template>
  <div class="space-y-8">
    <section class="grid gap-4 xl:grid-cols-[1.45fr_1fr]">
      <div class="group overflow-hidden rounded-2xl border border-slate-200 bg-slate-950 p-6 text-white shadow-xl shadow-slate-200/70 transition hover:-translate-y-0.5 dark:border-slate-800 dark:shadow-black/30">
        <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p class="text-sm font-medium text-slate-400">Caja actual</p>
            <h2 class="mt-3 text-4xl font-semibold tracking-tight">{{ formatCurrency(cajaActual) }}</h2>
            <div class="mt-4 flex flex-wrap items-center gap-2">
              <span :class="utilidadNeta >= 0 ? 'bg-emerald-400/10 text-emerald-300 ring-emerald-400/20' : 'bg-rose-400/10 text-rose-300 ring-rose-400/20'" class="rounded-full px-3 py-1 text-xs font-semibold ring-1">
                {{ utilidadNeta >= 0 ? '+' : '' }}{{ formatCurrency(utilidadNeta) }} utilidad neta
              </span>
              <span class="rounded-full bg-white/5 px-3 py-1 text-xs font-semibold text-slate-300 ring-1 ring-white/10">{{ trendLabel }}</span>
            </div>
          </div>
          <div class="h-24 w-full lg:w-56">
            <Line :data="sparklineData" :options="sparklineOptions" />
          </div>
        </div>

        <div class="mt-8 grid gap-3 sm:grid-cols-3">
          <div v-for="item in heroBreakdown" :key="item.label" class="rounded-xl bg-white/[0.04] p-4 ring-1 ring-white/10">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">{{ item.label }}</p>
            <p class="mt-2 text-lg font-semibold">{{ item.value }}</p>
          </div>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <KpiTile v-for="kpi in kpis" :key="kpi.label" v-bind="kpi" />
      </div>
    </section>

    <BaseCard content-class="p-0">
      <div class="flex flex-col gap-4 border-b border-slate-100 p-5 md:flex-row md:items-center md:justify-between dark:border-slate-800">
        <div>
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Tendencia financiera</p>
          <h2 class="mt-1 text-xl font-semibold text-slate-950 dark:text-white">Ingresos vs egresos</h2>
        </div>
        <div class="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-800 dark:bg-slate-900">
          <button v-for="option in rangeOptions" :key="option.value" :class="range === option.value ? 'bg-white text-slate-950 shadow-sm dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'" class="rounded-md px-3 py-1.5 text-sm font-semibold transition" type="button" @click="range = option.value">{{ option.label }}</button>
        </div>
      </div>
      <div class="h-[360px] p-4">
        <Line :data="mainChartData" :options="mainChartOptions" />
      </div>
    </BaseCard>

    <section class="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <BaseCard title="Resumen financiero" subtitle="Lectura ejecutiva de ingresos, gastos y cartera">
        <div class="grid gap-5 lg:grid-cols-[190px_1fr]">
          <div class="h-48">
            <Doughnut :data="financialDonutData" :options="donutOptions" />
          </div>
          <div class="space-y-3">
            <InsightRow label="Ingresos" :value="formatCurrency(metrics.ingresos_totales)" tone="emerald" badge="+12%" />
            <InsightRow label="Egresos" :value="formatCurrency(totalEgresos)" tone="rose" badge="-5%" />
            <InsightRow label="Utilidad neta" :value="formatCurrency(utilidadNeta)" :tone="utilidadNeta >= 0 ? 'sky' : 'rose'" :badge="utilidadNeta >= 0 ? 'saludable' : 'revisar'" />
            <InsightRow label="Saldo pendiente" :value="formatCurrency(metrics.saldo_pendiente)" tone="amber" badge="cartera" />
          </div>
        </div>
        <div class="mt-5 rounded-xl bg-slate-50 p-4 text-sm text-slate-600 dark:bg-slate-800/60 dark:text-slate-300">
          {{ financialInsight }}
        </div>
      </BaseCard>

      <BaseCard title="Estado de ordenes" subtitle="Distribucion operativa del taller">
        <div class="grid gap-5 lg:grid-cols-[210px_1fr]">
          <div class="h-56">
            <Doughnut :data="ordersDonutData" :options="donutOptions" />
          </div>
          <div class="grid content-center gap-3">
            <div v-for="item in orderStatus" :key="item.label" class="flex items-center justify-between rounded-xl border border-slate-100 p-3 dark:border-slate-800">
              <div class="flex items-center gap-3">
                <span :class="item.dot" class="h-2.5 w-2.5 rounded-full" />
                <span class="text-sm font-medium text-slate-700 dark:text-slate-200">{{ item.label }}</span>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-slate-950 dark:text-white">{{ item.value }}</p>
                <p class="text-xs text-slate-500">{{ item.percent }}%</p>
              </div>
            </div>
          </div>
        </div>
      </BaseCard>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
      <BaseCard title="Ordenes recientes" subtitle="Ultimos trabajos que requieren seguimiento" content-class="p-0">
        <div class="overflow-x-auto scrollbar-thin">
          <table class="min-w-full text-left text-sm">
            <thead class="border-b border-slate-100 bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:border-slate-800 dark:bg-slate-900">
              <tr>
                <th class="px-5 py-3">Orden</th>
                <th class="px-5 py-3">Cliente</th>
                <th class="px-5 py-3">Equipo</th>
                <th class="px-5 py-3">Estado</th>
                <th class="px-5 py-3">Saldo</th>
                <th class="px-5 py-3">Fecha</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              <tr v-for="orden in recentOrders" :key="orden.id" class="transition hover:bg-slate-50 dark:hover:bg-slate-800/50">
                <td class="px-5 py-4 font-semibold text-slate-950 dark:text-white">#{{ orden.id }}</td>
                <td class="px-5 py-4 text-slate-600 dark:text-slate-300">{{ clienteNombre(orden) }}</td>
                <td class="px-5 py-4 text-slate-600 dark:text-slate-300">{{ orden.equipo || orden.modelo || orden.dispositivo || 'Equipo' }}</td>
                <td class="px-5 py-4"><StatusBadge :value="orden.estado || 'recibido'" /></td>
                <td class="px-5 py-4 font-semibold text-slate-700 dark:text-slate-200">{{ formatCurrency(orden.saldo || orden.saldo_pendiente || 0) }}</td>
                <td class="px-5 py-4 text-slate-500">{{ formatDate(orden.created_at || orden.fecha) }}</td>
              </tr>
              <tr v-if="!recentOrders.length">
                <td colspan="6" class="px-5 py-8"><EmptyState icon="orders" title="Sin ordenes recientes" description="Cuando registres ordenes apareceran aqui." /></td>
              </tr>
            </tbody>
          </table>
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
    </section>

    <section class="grid gap-6 lg:grid-cols-3">
      <BaseCard title="Top clientes" subtitle="Clientes con mas ordenes">
        <WidgetList :items="topClientes" empty-title="Sin clientes" />
      </BaseCard>
      <BaseCard title="Metodos de pago" subtitle="Recaudo por canal">
        <WidgetList :items="paymentMethods" empty-title="Sin pagos" money />
      </BaseCard>
      <BaseCard title="Gastos por categoria" subtitle="Egresos mas relevantes">
        <WidgetList :items="expenseCategories" empty-title="Sin egresos" money />
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
import { computed, defineComponent, h, onMounted, reactive, ref } from 'vue'
import { Doughnut, Line } from 'vue-chartjs'
import AppIcon from '../components/AppIcon.vue'
import BaseCard from '../components/BaseCard.vue'
import EmptyState from '../components/EmptyState.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { movimientosCajaApi } from '../api/movimientosCajaApi'
import { clientesApi, dashboardApi, ordenesApi, pagosApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend, Filler)

const { formatCurrency, formatDate, formatNumber } = useFormatters()
const { run } = useApiState()
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

const totalEgresos = computed(() => egresos.value.reduce((sum, item) => sum + Number(item.valor || 0), 0))
const utilidadNeta = computed(() => Number(metrics.ingresos_totales || 0) - totalEgresos.value)
const cajaActual = computed(() => utilidadNeta.value)
const trendLabel = computed(() => (utilidadNeta.value >= 0 ? 'flujo positivo' : 'flujo bajo presion'))

const heroBreakdown = computed(() => [
  { label: 'Ingresos', value: formatCurrency(metrics.ingresos_totales) },
  { label: 'Egresos', value: formatCurrency(totalEgresos.value) },
  { label: 'Pendiente', value: formatCurrency(metrics.saldo_pendiente) },
])

const kpis = computed(() => [
  { label: 'Ingresos del mes', value: formatCurrency(metrics.ingresos_totales), icon: 'payments', tone: 'emerald', trend: '+12%', spark: [18, 24, 20, 34, 42, 38, 52] },
  { label: 'Egresos', value: formatCurrency(totalEgresos.value), icon: 'cash', tone: 'rose', trend: '-5%', spark: [28, 22, 31, 26, 18, 24, 20] },
  { label: 'Ordenes activas', value: formatNumber(metrics.ordenes_activas), icon: 'orders', tone: 'sky', trend: `${formatNumber(metrics.total_ordenes)} total`, spark: [8, 12, 10, 14, 18, 17, 20] },
  { label: 'Saldo pendiente', value: formatCurrency(metrics.saldo_pendiente), icon: 'cash', tone: 'amber', trend: 'cartera', spark: [34, 32, 36, 31, 29, 26, 24] },
])

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
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.12)',
      fill: true,
      tension: 0.42,
      pointRadius: 0,
      pointHoverRadius: 5,
    },
    {
      label: 'Egresos',
      data: dailySeries.value.egresos,
      borderColor: '#f43f5e',
      backgroundColor: 'rgba(244, 63, 94, 0.10)',
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

const sparklineData = computed(() => ({
  labels: dailySeries.value.labels,
  datasets: [
    {
      data: dailySeries.value.ingresos.map((value, index) => value - (dailySeries.value.egresos[index] || 0)),
      borderColor: '#5eead4',
      backgroundColor: 'rgba(94, 234, 212, 0.18)',
      fill: true,
      tension: 0.45,
      pointRadius: 0,
    },
  ],
}))

const sparklineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { enabled: false } },
  scales: { x: { display: false }, y: { display: false } },
}

const financialDonutData = computed(() => ({
  labels: ['Ingresos', 'Egresos', 'Pendiente'],
  datasets: [
    {
      data: [metrics.ingresos_totales, totalEgresos.value, metrics.saldo_pendiente].map((value) => Math.max(Number(value), 0)),
      backgroundColor: ['#10b981', '#f43f5e', '#f59e0b'],
      borderWidth: 0,
      hoverOffset: 8,
    },
  ],
}))

const orderStatus = computed(() => {
  const received = countOrders(['recibido', 'recibida', 'pendiente'])
  const repair = countOrders(['reparando', 'reparacion', 'proceso'])
  const ready = countOrders(['listo', 'reparado'])
  const delivered = countOrders(['entregado', 'entregada']) || metrics.ordenes_entregadas
  const total = Math.max(received + repair + ready + delivered, metrics.total_ordenes, 1)

  return [
    { label: 'Recibidas', value: received, percent: Math.round((received / total) * 100), dot: 'bg-violet-500' },
    { label: 'Reparacion', value: repair, percent: Math.round((repair / total) * 100), dot: 'bg-sky-500' },
    { label: 'Listas', value: ready, percent: Math.round((ready / total) * 100), dot: 'bg-amber-500' },
    { label: 'Entregadas', value: delivered, percent: Math.round((delivered / total) * 100), dot: 'bg-emerald-500' },
  ]
})

const ordersDonutData = computed(() => ({
  labels: orderStatus.value.map((item) => item.label),
  datasets: [
    {
      data: orderStatus.value.map((item) => item.value),
      backgroundColor: ['#8b5cf6', '#0ea5e9', '#f59e0b', '#10b981'],
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

const financialInsight = computed(() => {
  if (utilidadNeta.value >= 0) {
    return `El negocio conserva margen positivo: por cada peso de ingreso, los egresos representan aproximadamente ${expenseRatio.value}%.`
  }

  return `Los egresos superan los ingresos registrados. Revisa categorias de gasto y cartera pendiente para recuperar margen.`
})

const expenseRatio = computed(() => {
  if (!metrics.ingresos_totales) return 0
  return Math.round((totalEgresos.value / metrics.ingresos_totales) * 100)
})

const recentOrders = computed(() => [...ordenes.value].sort(sortByDate).slice(0, 6))

const timeline = computed(() => {
  const events = [
    ...pagos.value.map((pago) => ({
      id: `pago-${pago.id}`,
      date: pago.created_at || pago.fecha,
      icon: 'payments',
      tone: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300',
      title: 'Ingreso registrado',
      description: formatCurrency(pago.valor || pago.monto || pago.total || 0),
    })),
    ...egresos.value.map((egreso) => ({
      id: `egreso-${egreso.id}`,
      date: egreso.created_at,
      icon: 'cash',
      tone: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
      title: 'Egreso registrado',
      description: `${egreso.categoria || 'gasto'} · ${formatCurrency(egreso.valor)}`,
    })),
    ...ordenes.value.map((orden) => ({
      id: `orden-${orden.id}`,
      date: orden.created_at || orden.fecha,
      icon: 'orders',
      tone: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300',
      title: orden.estado?.toLowerCase().includes('entreg') ? 'Orden entregada' : 'Orden creada',
      description: `#${orden.id} · ${orden.equipo || orden.modelo || 'Equipo'}`,
    })),
  ]

  return events.sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0)).slice(0, 7).map((event) => ({
    ...event,
    time: formatDate(event.date),
  }))
})

const topClientes = computed(() => {
  const totals = ordenes.value.reduce((acc, orden) => {
    const name = clienteNombre(orden)
    acc[name] = (acc[name] || 0) + 1
    return acc
  }, {})

  return toWidgetItems(totals, false)
})

const paymentMethods = computed(() => {
  const totals = pagos.value.reduce((acc, pago) => {
    const method = pago.metodo_pago || pago.metodo || 'Sin metodo'
    acc[method] = (acc[method] || 0) + Number(pago.valor || pago.monto || pago.total || 0)
    return acc
  }, {})

  return toWidgetItems(totals, true)
})

const expenseCategories = computed(() => {
  const totals = egresos.value.reduce((acc, egreso) => {
    const category = egreso.categoria || 'otros'
    acc[category] = (acc[category] || 0) + Number(egreso.valor || 0)
    return acc
  }, {})

  return toWidgetItems(totals, true)
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

function sortByDate(a, b) {
  return new Date(b.created_at || b.fecha || 0) - new Date(a.created_at || a.fecha || 0)
}

function toWidgetItems(totals, money) {
  const max = Math.max(...Object.values(totals), 1)
  return Object.entries(totals)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([label, value]) => ({
      label,
      value: money ? formatCurrency(value) : formatNumber(value),
      percent: Math.max((value / max) * 100, 6),
    }))
}

function formatShortMoney(value) {
  if (value >= 1000000) return `$${Math.round(value / 1000000)}M`
  if (value >= 1000) return `$${Math.round(value / 1000)}K`
  return `$${value}`
}

onMounted(async () => {
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
})

const KpiTile = defineComponent({
  props: {
    label: String,
    value: String,
    icon: String,
    tone: String,
    trend: String,
    spark: Array,
  },
  setup(props) {
    const colors = {
      emerald: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300',
      rose: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
      sky: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300',
      amber: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300',
    }

    return () =>
      h('div', { class: 'rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900' }, [
        h('div', { class: 'flex items-start justify-between gap-3' }, [
          h('div', [h('p', { class: 'text-sm font-medium text-slate-500 dark:text-slate-400' }, props.label), h('p', { class: 'mt-2 text-2xl font-semibold text-slate-950 dark:text-white' }, props.value)]),
          h('div', { class: `flex h-10 w-10 items-center justify-center rounded-xl ${colors[props.tone]}` }, [h(AppIcon, { name: props.icon })]),
        ]),
        h('div', { class: 'mt-5 flex items-end justify-between gap-3' }, [
          h('span', { class: 'rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300' }, props.trend),
          h('div', { class: 'flex h-10 items-end gap-1' }, props.spark.map((value, index) => h('span', { key: index, class: 'w-1.5 rounded-full bg-slate-300 dark:bg-slate-700', style: { height: `${value}%` } }))),
        ]),
      ])
  },
})

const InsightRow = defineComponent({
  props: { label: String, value: String, tone: String, badge: String },
  setup(props) {
    const dots = {
      emerald: 'bg-emerald-500',
      rose: 'bg-rose-500',
      sky: 'bg-sky-500',
      amber: 'bg-amber-500',
    }

    return () =>
      h('div', { class: 'flex items-center justify-between rounded-xl border border-slate-100 p-3 dark:border-slate-800' }, [
        h('div', { class: 'flex items-center gap-3' }, [h('span', { class: `h-2.5 w-2.5 rounded-full ${dots[props.tone]}` }), h('span', { class: 'text-sm font-medium text-slate-700 dark:text-slate-200' }, props.label)]),
        h('div', { class: 'text-right' }, [h('p', { class: 'text-sm font-semibold text-slate-950 dark:text-white' }, props.value), h('p', { class: 'text-xs text-slate-500' }, props.badge)]),
      ])
  },
})

const WidgetList = defineComponent({
  props: { items: Array, emptyTitle: String, money: Boolean },
  setup(props) {
    return () =>
      props.items?.length
        ? h('div', { class: 'space-y-4' }, props.items.map((item) =>
            h('div', { key: item.label }, [
              h('div', { class: 'mb-2 flex items-center justify-between gap-3 text-sm' }, [
                h('span', { class: 'truncate font-medium capitalize text-slate-700 dark:text-slate-200' }, item.label),
                h('span', { class: 'font-semibold text-slate-950 dark:text-white' }, item.value),
              ]),
              h('div', { class: 'h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800' }, [h('div', { class: 'h-full rounded-full bg-slate-950 dark:bg-white', style: { width: `${item.percent}%` } })]),
            ]),
          ))
        : h(EmptyState, { icon: 'dashboard', title: props.emptyTitle, description: 'Aparecera cuando exista informacion suficiente.' })
  },
})
</script>
