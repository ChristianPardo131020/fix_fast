<template>
  <div class="space-y-6">
    <PageHeader title="Resumen general" subtitle="El estado de tu taller, sin vueltas." />

    <FilterBar label="Periodo">
      <DateRangePicker v-model="dateRange" />
    </FilterBar>

    <!-- Acciones rapidas: llevan a la vista correspondiente con el modal
         de creacion ya abierto (?crear=1), en vez de duplicar los 3
         formularios aca. Siempre visibles, no dependen de que el
         dashboard haya cargado. -->
    <section class="flex flex-wrap items-center gap-3">
      <span class="w-full text-xs font-semibold uppercase tracking-wide text-slate-400 sm:w-auto">Acciones rapidas</span>
      <BaseButton icon="orders" @click="router.push({ name: 'ordenes', query: { crear: '1' } })">Nueva orden</BaseButton>
      <BaseButton variant="secondary" icon="payments" @click="router.push({ name: 'pagos', query: { crear: '1' } })">Registrar pago</BaseButton>
      <BaseButton variant="secondary" icon="trend-down" @click="router.push({ name: 'caja', query: { crear: '1' } })">Nuevo egreso</BaseButton>
    </section>

    <div v-if="loading" class="space-y-6">
      <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <div v-for="n in 5" :key="n" class="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
          <div class="skeleton h-3 w-24 rounded" />
          <div class="skeleton mt-3 h-7 w-20 rounded" />
        </div>
      </section>
      <div class="skeleton h-[400px] rounded-xl border border-slate-200 dark:border-slate-800" />
      <section class="grid gap-6 xl:grid-cols-2">
        <div class="skeleton h-72 rounded-xl border border-slate-200 dark:border-slate-800" />
        <div class="skeleton h-72 rounded-xl border border-slate-200 dark:border-slate-800" />
      </section>
    </div>

    <div v-else-if="dashboard" class="space-y-6">
      <!-- Fila 1: KPIs principales, la pregunta "como va el negocio" -->
      <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard
          label="Ingresos del periodo"
          :value="formatCurrency(dashboard.kpis.ingresos.valor)"
          icon="payments"
          tone="brand"
          :trend="dashboard.kpis.ingresos"
          :desglose="dashboard.kpis.ingresos.desglose"
          :hint="periodo.label"
        />
        <StatCard
          label="Utilidad del periodo"
          :value="formatCurrency(dashboard.kpis.utilidad.valor)"
          icon="wallet"
          :tone="Number(dashboard.kpis.utilidad.valor) >= 0 ? 'green' : 'rose'"
          :trend="dashboard.kpis.utilidad"
          :desglose="dashboard.kpis.utilidad.desglose"
          :hint="`Margen: ${dashboard.kpis.margen_pct.valor}%`"
        />
        <StatCard
          label="Saldo por cobrar"
          :value="formatCurrency(dashboard.kpis.saldo_pendiente.valor)"
          icon="cash"
          tone="orange"
          :trend="dashboard.kpis.saldo_pendiente"
          :desglose="dashboard.kpis.saldo_pendiente.desglose"
          invert
          hint="De ordenes del periodo"
        />
        <StatCard
          label="Equipos en reparacion"
          :value="formatNumber(dashboard.kpis.equipos_reparacion.valor)"
          icon="wrench"
          tone="sky"
          :trend="dashboard.kpis.equipos_reparacion"
          :desglose="dashboard.kpis.equipos_reparacion.desglose"
          hint="Ingresaron en el periodo"
        />
        <StatCard
          label="Listos para entregar"
          :value="formatNumber(dashboard.kpis.equipos_listos.valor)"
          icon="check"
          tone="green"
          :trend="dashboard.kpis.equipos_listos"
          :desglose="dashboard.kpis.equipos_listos.desglose"
          hint="Ingresaron en el periodo"
        />
      </section>

      <!-- Fila 2: tendencia -->
      <CashflowChart :model-value="chartGranularity" :data="dashboard.cashflow" @update:model-value="onGranularityChange" />

      <!-- Fila 3: estados de ordenes + metodos de pago -->
      <section class="grid gap-6 xl:grid-cols-2">
        <OrdersStatusPanel :data="dashboard.orders" />
        <PaymentMethodsPanel :data="dashboard.payments" />
      </section>

      <!-- Fila 4: flujo financiero + alertas (reemplaza los "top") -->
      <section class="grid gap-6 xl:grid-cols-2">
        <FinancialFlowPanel :kpis="dashboard.kpis" :performance="dashboard.performance" :cashflow="dashboard.cashflow" />
        <AlertsPanel :alerts="dashboard.alerts" />
      </section>

      <!-- Fila 5: KPIs secundarios -->
      <section>
        <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">Indicadores operativos</p>
        <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <StatCard
            label="Tiempo promedio de reparacion"
            :value="`${dashboard.performance.tiempo_promedio_reparacion_dias.valor} dias`"
            icon="timer"
            tone="brand"
            :trend="dashboard.performance.tiempo_promedio_reparacion_dias"
            invert
            hint="Ingreso a entrega, ordenes entregadas en el periodo"
          />
          <StatCard
            label="Equipos atrasados"
            :value="formatNumber(dashboard.performance.equipos_atrasados.valor)"
            icon="alert"
            tone="rose"
            :trend="dashboard.performance.equipos_atrasados"
            invert
            hint="Mas de 7 dias abiertos, en vivo"
          />
          <StatCard
            label="Ticket promedio"
            :value="formatCurrency(dashboard.performance.ticket_promedio.valor)"
            icon="cash"
            tone="teal"
            :trend="dashboard.performance.ticket_promedio"
            hint="Por transaccion, periodo actual"
          />
          <StatCard
            label="Conversion"
            :value="`${dashboard.performance.conversion_pct.valor}%`"
            icon="gauge"
            tone="purple"
            :trend="dashboard.performance.conversion_pct"
            hint="Ordenes del periodo ya entregadas"
          />
          <StatCard
            label="Gastos del periodo"
            :value="formatCurrency(dashboard.performance.gastos_periodo.valor)"
            icon="trend-down"
            tone="rose"
            :trend="dashboard.performance.gastos_periodo"
            :desglose="dashboard.performance.gastos_periodo.desglose"
            invert
            hint="Egresos de caja"
          />
          <StatCard
            label="Saldo disponible"
            :value="formatCurrency(dashboard.performance.saldo_disponible.valor)"
            icon="landmark"
            tone="slate"
            :trend="dashboard.performance.saldo_disponible"
            hint="Caja acumulada a hoy"
          />
        </div>
      </section>
    </div>

    <BaseCard v-else content-class="p-8">
      <EmptyState
        icon="alert"
        title="No se pudo cargar el dashboard"
        :description="loadError || 'Intenta de nuevo en unos segundos.'"
      />
      <div class="mt-4 flex justify-center">
        <BaseButton variant="secondary" @click="loadDashboard">Reintentar</BaseButton>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AlertsPanel from '../components/dashboard/AlertsPanel.vue'
import CashflowChart from '../components/dashboard/CashflowChart.vue'
import FinancialFlowPanel from '../components/dashboard/FinancialFlowPanel.vue'
import OrdersStatusPanel from '../components/dashboard/OrdersStatusPanel.vue'
import PaymentMethodsPanel from '../components/dashboard/PaymentMethodsPanel.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import DateRangePicker from '../components/DateRangePicker.vue'
import EmptyState from '../components/EmptyState.vue'
import FilterBar from '../components/FilterBar.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import { dashboardApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

const { formatCurrency, formatNumber } = useFormatters()
const { run } = useApiState()
const router = useRouter()

import { toISO } from '../utils/dateRanges'

const now = new Date()
const dateRange = ref({
  desde: toISO(now),
  hasta: toISO(now),
})
const chartGranularity = ref(null) // null = que el backend elija el default segun el periodo

const dashboard = ref(null)
const loading = ref(true)
const loadError = ref('')

const periodo = computed(() => dashboard.value?.periodo || { label: '' })

// Si el usuario clickeo explicitamente Dia/Semana/Mes/Año, esa eleccion
// se respeta al cambiar de periodo. Si nunca la toco, cada cambio de
// rango vuelve a pedirle al backend su default inteligente.
const granularityTouchedByUser = ref(false)

// Convierte el rango desde/hasta en los params year/month/day que
// espera el endpoint del dashboard.
function rangeToParams(range) {
  if (!range.desde && !range.hasta) {
    return { year: now.getFullYear() }
  }
  const [sy, sm, sd] = (range.desde || range.hasta).split('-').map(Number)
  const [ey, em, ed] = (range.hasta || range.desde).split('-').map(Number)

  // Mismo día → year + month + day
  if (range.desde === range.hasta) {
    return { year: sy, month: sm, day: sd }
  }

  // Mes completo (1ro al último día del mismo mes/año)
  if (sd === 1 && sy === ey && sm === em) {
    const lastDay = new Date(sy, sm, 0).getDate()
    if (ed === lastDay) return { year: sy, month: sm }
  }

  // Año completo (1 Ene - 31 Dic)
  if (sm === 1 && sd === 1 && em === 12 && ed === 31 && sy === ey) {
    return { year: sy }
  }

  // Rango arbitrario: usar el año de inicio y filtrar en frontend si
  // el backend no soporta rango libre; por ahora mandamos solo year
  // para traer todo el año y luego la vista filtra localmente.
  return { year: sy, desde: range.desde, hasta: range.hasta }
}

async function loadDashboard() {
  loading.value = true
  loadError.value = ''
  try {
    const params = rangeToParams(dateRange.value)
    if (granularityTouchedByUser.value) params.chart_granularity = chartGranularity.value

    const response = await run(() => dashboardApi.get(params))

    // Chequeo de forma antes de asignar: si la respuesta no trae lo que
    // se espera (backend caido a mitad de un deploy, proxy devolviendo
    // otra cosa, etc.) se trata como error en vez de dejar que un
    // "undefined.algo" reviente el render mas abajo.
    if (!response.data?.kpis || !response.data?.cashflow) {
      throw new Error('La respuesta del servidor no tiene el formato esperado.')
    }

    dashboard.value = response.data
    chartGranularity.value = response.data.cashflow.granularidad
  } catch (err) {
    dashboard.value = null
    loadError.value = err.response?.data?.detail || err.message || 'No se pudo cargar el dashboard.'
  } finally {
    loading.value = false
  }
}

function onGranularityChange(value) {
  granularityTouchedByUser.value = true
  chartGranularity.value = value
  loadDashboard()
}

watch(dateRange, loadDashboard, { deep: true })

onMounted(loadDashboard)
</script>
