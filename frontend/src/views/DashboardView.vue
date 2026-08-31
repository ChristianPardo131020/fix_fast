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
            v-if="selectedMonth !== null"
            v-model="selectedDay"
            class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200"
          >
            <option :value="null">Todos los días</option>
            <option v-for="d in daysInSelectedMonth" :key="d" :value="d">{{ d }}</option>
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
import EmptyState from '../components/EmptyState.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import { dashboardApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

const { formatCurrency, formatNumber } = useFormatters()
const { run } = useApiState()
const router = useRouter()

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth() + 1) // 1-12, null = todo el año
const selectedDay = ref(now.getDate()) // por defecto hoy
const chartGranularity = ref(null) // null = que el backend elija el default segun el periodo

const daysInSelectedMonth = computed(() => {
  if (!selectedMonth.value) return 0
  return new Date(selectedYear.value, selectedMonth.value, 0).getDate()
})

// Si el usuario cambia mes/año, resetear dia si queda invalido
watch([selectedYear, selectedMonth], () => {
  selectedDay.value = null
})

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
const loadError = ref('')

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
  loadError.value = ''
  try {
    const params = {
      year: selectedYear.value,
    }
    if (selectedMonth.value !== null) params.month = selectedMonth.value
    if (selectedDay.value !== null) params.day = selectedDay.value
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

watch([selectedYear, selectedMonth, selectedDay], loadDashboard)

onMounted(loadDashboard)
</script>
