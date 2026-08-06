<template>
  <div class="space-y-6">
    <PageHeader title="Resumen general" subtitle="El estado de tu taller, sin vueltas.">
      <template #actions>
        <div class="flex items-center gap-2">
          <select
            v-model="selectedMonth"
            class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
          >
            <option :value="null">Todos los meses</option>
            <option v-for="(mes, index) in meses" :key="mes" :value="index + 1">{{ mes }}</option>
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

    <div v-if="loading" class="space-y-6">
      <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <div v-for="n in 5" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
          <div class="h-3 w-24 rounded bg-slate-200 dark:bg-slate-800" />
          <div class="mt-3 h-7 w-20 rounded bg-slate-200 dark:bg-slate-800" />
        </div>
      </section>
      <div class="h-[400px] animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900" />
      <section class="grid gap-6 xl:grid-cols-2">
        <div class="h-72 animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900" />
        <div class="h-72 animate-pulse rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900" />
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
          :hint="periodo.label"
        />
        <StatCard
          label="Utilidad del periodo"
          :value="formatCurrency(dashboard.kpis.utilidad.valor)"
          icon="wallet"
          :tone="Number(dashboard.kpis.utilidad.valor) >= 0 ? 'green' : 'rose'"
          :trend="dashboard.kpis.utilidad"
          :hint="`Margen: ${dashboard.kpis.margen_pct.valor}%`"
        />
        <StatCard
          label="Saldo por cobrar"
          :value="formatCurrency(dashboard.kpis.saldo_pendiente.valor)"
          icon="cash"
          tone="orange"
          :trend="dashboard.kpis.saldo_pendiente"
          invert
          hint="De ordenes del periodo"
        />
        <StatCard
          label="Equipos en reparacion"
          :value="formatNumber(dashboard.kpis.equipos_reparacion.valor)"
          icon="wrench"
          tone="sky"
          :trend="dashboard.kpis.equipos_reparacion"
          hint="Ingresaron en el periodo"
        />
        <StatCard
          label="Listos para entregar"
          :value="formatNumber(dashboard.kpis.equipos_listos.valor)"
          icon="check"
          tone="green"
          :trend="dashboard.kpis.equipos_listos"
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
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import AlertsPanel from '../components/dashboard/AlertsPanel.vue'
import CashflowChart from '../components/dashboard/CashflowChart.vue'
import FinancialFlowPanel from '../components/dashboard/FinancialFlowPanel.vue'
import OrdersStatusPanel from '../components/dashboard/OrdersStatusPanel.vue'
import PaymentMethodsPanel from '../components/dashboard/PaymentMethodsPanel.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import { dashboardApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

const { formatCurrency, formatNumber } = useFormatters()
const { run } = useApiState()

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth() + 1) // 1-12, null = todo el año
const chartGranularity = ref(null) // null = que el backend elija el default segun el periodo

// El backend calcula todo — el frontend solo pinta "dashboard" tal cual
// llega. availableYears es la unica lista que se arma en el cliente, y
// no es un calculo de negocio: son opciones de un <select>.
const availableYears = computed(() => {
  const years = new Set([now.getFullYear()])
  if (dashboard.value) years.add(dashboard.value.periodo.year)
  return [...years].sort((a, b) => b - a)
})

const dashboard = ref(null)
const loading = ref(true)

const periodo = computed(() => dashboard.value?.periodo || { label: '' })

// Si el usuario clickeo explicitamente Dia/Semana/Mes/Año, esa eleccion
// se respeta al cambiar de periodo. Si nunca la toco, cada cambio de
// Mes/Año vuelve a pedirle al backend su default inteligente (dia para
// un mes puntual, mes para "todos los meses") en vez de arrastrar una
// granularidad que ya no tiene sentido para el nuevo rango (ej. ver
// 365 puntos diarios de golpe al pasar de un mes a "todo el año").
const granularityTouchedByUser = ref(false)

async function loadDashboard() {
  loading.value = true
  try {
    const response = await run(() => dashboardApi.get({
      year: selectedYear.value,
      month: selectedMonth.value,
      chart_granularity: granularityTouchedByUser.value ? chartGranularity.value : null,
    }))
    dashboard.value = response.data
    chartGranularity.value = response.data.cashflow.granularidad
  } finally {
    loading.value = false
  }
}

function onGranularityChange(value) {
  granularityTouchedByUser.value = true
  chartGranularity.value = value
  loadDashboard()
}

watch([selectedYear, selectedMonth], loadDashboard)

onMounted(loadDashboard)
</script>
