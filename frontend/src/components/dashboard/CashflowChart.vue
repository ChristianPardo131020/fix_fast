<template>
  <BaseCard content-class="p-0">
    <div class="flex flex-col gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between dark:border-slate-800">
      <div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Tendencia financiera</p>
        <h2 class="mt-0.5 text-xl font-semibold text-slate-950 dark:text-white">Ingresos, egresos y utilidad</h2>
      </div>
      <div class="inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-800 dark:bg-slate-900">
        <button
          v-for="option in granularityOptions"
          :key="option.value"
          type="button"
          class="rounded-md px-3 py-1.5 text-sm font-semibold transition"
          :class="modelValue === option.value ? 'bg-white text-slate-950 shadow-sm dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900 dark:hover:text-slate-200'"
          @click="$emit('update:modelValue', option.value)"
        >
          {{ option.label }}
        </button>
      </div>
    </div>
    <div class="h-[320px] p-4">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import BaseCard from '../BaseCard.vue'
import { useFormatters } from '../../composables/useFormatters'

const props = defineProps({
  data: { type: Object, required: true }, // { granularidad, puntos: [{fecha, ingresos, egresos, utilidad}] }
  modelValue: { type: String, required: true }, // granularidad activa: day|week|month|year
})

defineEmits(['update:modelValue'])

const { formatCurrency } = useFormatters()

const granularityOptions = [
  { label: 'Dia', value: 'day' },
  { label: 'Semana', value: 'week' },
  { label: 'Mes', value: 'month' },
  { label: 'Año', value: 'year' },
]

function formatLabel(fecha) {
  const date = new Date(`${fecha}T00:00:00`)
  if (props.data.granularidad === 'day') return `${date.getDate()}`
  if (props.data.granularidad === 'week') return `${date.getDate()}/${date.getMonth() + 1}`
  if (props.data.granularidad === 'month') return date.toLocaleDateString('es-CO', { month: 'short' })
  return `${date.getFullYear()}`
}

const chartData = computed(() => ({
  labels: props.data.puntos.map((punto) => formatLabel(punto.fecha)),
  datasets: [
    {
      label: 'Ingresos',
      data: props.data.puntos.map((punto) => Number(punto.ingresos)),
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34, 197, 94, 0.12)',
      fill: true,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 5,
    },
    {
      label: 'Egresos',
      data: props.data.puntos.map((punto) => Number(punto.egresos)),
      borderColor: '#ef4444',
      backgroundColor: 'rgba(239, 68, 68, 0.10)',
      fill: true,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 5,
    },
    {
      label: 'Utilidad',
      data: props.data.puntos.map((punto) => Number(punto.utilidad)),
      borderColor: '#3b66f5',
      backgroundColor: 'transparent',
      borderDash: [5, 4],
      fill: false,
      tension: 0.4,
      pointRadius: 0,
      pointHoverRadius: 5,
    },
  ],
}))

const chartOptions = {
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
    y: {
      grid: { color: 'rgba(148, 163, 184, 0.16)' },
      ticks: {
        color: '#94a3b8',
        callback: (value) => {
          if (Math.abs(value) >= 1_000_000) return `$${Math.round(value / 1_000_000)}M`
          if (Math.abs(value) >= 1_000) return `$${Math.round(value / 1_000)}K`
          return `$${value}`
        },
      },
    },
  },
}
</script>
