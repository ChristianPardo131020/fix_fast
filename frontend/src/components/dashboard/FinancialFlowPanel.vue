<template>
  <BaseCard title="Flujo financiero" subtitle="De donde viene la plata y que queda" content-class="p-5">
    <div>
      <template v-for="(step, index) in steps" :key="step.label">
        <div class="flex items-center justify-between gap-3 rounded-xl px-3 py-2.5" :class="step.bg">
          <div class="flex items-center gap-2.5">
            <AppIcon :name="step.icon" class="h-4 w-4" :class="step.iconColor" />
            <span class="text-sm font-medium" :class="step.textColor">{{ step.label }}</span>
          </div>
          <span class="text-sm font-semibold" :class="step.textColor">{{ step.value }}</span>
        </div>
        <div v-if="index < steps.length - 1" class="flex justify-center py-1">
          <AppIcon name="arrow-down" class="h-3.5 w-3.5 text-slate-300 dark:text-slate-600" />
        </div>
      </template>
    </div>

    <div class="mt-5">
      <p class="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">Utilidad acumulada del periodo</p>
      <div class="h-24">
        <Line :data="chartData" :options="chartOptions" />
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import AppIcon from '../AppIcon.vue'
import BaseCard from '../BaseCard.vue'
import { useFormatters } from '../../composables/useFormatters'

const props = defineProps({
  kpis: { type: Object, required: true },
  performance: { type: Object, required: true },
  cashflow: { type: Object, required: true },
})

const { formatCurrency } = useFormatters()

const steps = computed(() => {
  const utilidadPositiva = Number(props.kpis.utilidad.valor) >= 0

  return [
    { label: 'Ingresos', value: formatCurrency(props.kpis.ingresos.valor), icon: 'trend-up', bg: 'bg-green-50 dark:bg-green-500/10', textColor: 'text-green-800 dark:text-green-300', iconColor: 'text-green-600 dark:text-green-400' },
    { label: 'Egresos', value: formatCurrency(props.performance.gastos_periodo.valor), icon: 'trend-down', bg: 'bg-red-50 dark:bg-red-500/10', textColor: 'text-red-800 dark:text-red-300', iconColor: 'text-red-600 dark:text-red-400' },
    {
      label: 'Utilidad',
      value: formatCurrency(props.kpis.utilidad.valor),
      icon: utilidadPositiva ? 'trend-up' : 'trend-down',
      bg: utilidadPositiva ? 'bg-brand-50 dark:bg-brand-500/10' : 'bg-red-50 dark:bg-red-500/10',
      textColor: utilidadPositiva ? 'text-brand-800 dark:text-brand-300' : 'text-red-800 dark:text-red-300',
      iconColor: utilidadPositiva ? 'text-brand-600 dark:text-brand-400' : 'text-red-600 dark:text-red-400',
    },
    { label: 'Margen', value: `${props.kpis.margen_pct.valor}%`, icon: 'percent', bg: 'bg-purple-50 dark:bg-purple-500/10', textColor: 'text-purple-800 dark:text-purple-300', iconColor: 'text-purple-600 dark:text-purple-400' },
  ]
})

const chartData = computed(() => ({
  labels: props.cashflow.puntos.map((punto) => punto.fecha),
  datasets: [
    {
      data: props.cashflow.puntos.map((punto) => Number(punto.utilidad_acumulada)),
      borderColor: '#3b66f5',
      backgroundColor: 'rgba(59, 102, 245, 0.12)',
      fill: true,
      tension: 0.4,
      pointRadius: 0,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#020617',
      padding: 10,
      cornerRadius: 8,
      callbacks: { label: (context) => formatCurrency(context.parsed.y) },
    },
  },
  scales: {
    x: { display: false },
    y: { display: false },
  },
}
</script>
