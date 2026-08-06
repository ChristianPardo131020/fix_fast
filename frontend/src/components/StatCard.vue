<template>
  <BaseCard content-class="p-5" class="transition hover:-translate-y-0.5 hover:shadow-lift">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0">
        <p class="truncate text-sm font-medium text-slate-500 dark:text-slate-400">{{ label }}</p>
        <p class="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">{{ value }}</p>
      </div>
      <div :class="toneClass" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl">
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
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import BaseCard from './BaseCard.vue'

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
})

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
