<template>
  <BaseCard content-class="p-5" class="group relative transition hover:-translate-y-0.5 hover:shadow-lift hover:z-50" :class="{ 'cursor-help': desglose.length }">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0">
        <p class="truncate text-sm font-medium text-slate-500 dark:text-slate-400">{{ label }}</p>
        <p class="mt-2 text-2xl font-semibold tabular-nums tracking-tight text-slate-950 dark:text-white">{{ animatedValue }}</p>
      </div>
      <div :class="toneClass" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-110">
        <AppIcon :name="icon" class="h-5 w-5" />
      </div>
    </div>

    <div v-if="trend" class="mt-3">
      <span class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold" :class="trendClasses">
        <AppIcon :name="trendIcon" class="h-3 w-3" />
        {{ trendLabel }}
      </span>
    </div>

    <p v-if="hint" class="mt-3 text-xs text-slate-500 dark:text-slate-400">{{ hint }}</p>

    <!-- Resumen al pasar el mouse: desglose del KPI (ingresos por origen,
         egresos por categoria, ordenes por estado, etc.). Solo aparece si
         el backend mando un desglose para esta metrica. -->
    <div
      v-if="desglose.length"
      class="pointer-events-none absolute inset-x-0 top-full z-30 mt-2 translate-y-1 opacity-0 transition duration-150 group-hover:translate-y-0 group-hover:opacity-100"
    >
      <div class="rounded-xl border border-slate-200 bg-white p-3 shadow-lift dark:border-slate-700 dark:bg-slate-800">
        <p class="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">{{ label }}</p>
        <dl class="space-y-1">
          <div
            v-for="row in desglose"
            :key="row.label"
            class="flex items-center justify-between gap-6 text-xs text-slate-600 dark:text-slate-300"
          >
            <dt>{{ row.label }}</dt>
            <dd class="font-medium tabular-nums text-slate-900 dark:text-white">{{ formatRow(row) }}</dd>
          </div>
        </dl>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import BaseCard from './BaseCard.vue'
import { useFormatters } from '../composables/useFormatters'
import { useCountUp } from '../composables/useCountUp'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  icon: { type: String, default: 'dashboard' },
  tone: { type: String, default: 'teal' },
  hint: { type: String, default: '' },
  // { variacion_pct: number|null, tendencia: 'up'|'down'|'flat' } — el
  // shape exacto que devuelve el backend (Metric/MetricInt en
  // dashboard_schema.py), se pasa tal cual sin transformar.
  trend: { type: Object, default: null },
  // Para metricas donde "subir" es malo (ej. gastos, equipos atrasados):
  // invierte el color del badge sin invertir la flecha/el signo.
  invert: { type: Boolean, default: false },
  // Filas del resumen que se muestra al pasar el mouse. Shape del backend:
  // { label, valor, formato: 'moneda'|'entero'|'porcentaje' }.
  desglose: { type: Array, default: () => [] },
})

const { formatCurrency, formatNumber } = useFormatters()

// El KPI entra ya formateado como string ("$1.234.567", "12%", "3 dias");
// useCountUp lo anima sin cambiar la prop `value` ni su formato.
const animatedValue = useCountUp(() => props.value)

function formatRow(row) {
  if (row.formato === 'entero') return formatNumber(row.valor)
  if (row.formato === 'porcentaje') return `${row.valor}%`
  return formatCurrency(row.valor)
}

const toneClass = computed(() => ({
  teal: 'bg-teal-100 text-teal-700 dark:bg-teal-500/15 dark:text-teal-300',
  slate: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300',
  rose: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
  sky: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300',
  brand: 'bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300',
  green: 'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300',
  orange: 'bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300',
  purple: 'bg-purple-100 text-purple-700 dark:bg-purple-500/15 dark:text-purple-300',
}[props.tone]))

const trendIcon = computed(() => {
  if (!props.trend) return 'minus'
  return { up: 'arrow-up-right', down: 'arrow-down-right', flat: 'minus' }[props.trend.tendencia] || 'minus'
})

const trendLabel = computed(() => {
  if (!props.trend) return ''
  const pct = props.trend.variacion_pct
  if (pct === null || pct === undefined) return 'Sin datos previos'
  const signo = Number(pct) > 0 ? '+' : ''
  return `${signo}${pct}% vs periodo anterior`
})

const trendClasses = computed(() => {
  if (!props.trend) return ''
  let direction = props.trend.tendencia
  if (props.invert && direction !== 'flat') {
    direction = direction === 'up' ? 'down' : 'up'
  }
  return {
    up: 'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300',
    down: 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300',
    flat: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
  }[direction]
})
</script>
