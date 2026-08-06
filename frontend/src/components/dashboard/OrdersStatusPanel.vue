<template>
  <BaseCard title="Estados de ordenes" subtitle="Distribucion operativa del periodo">
    <div class="flex flex-col items-center gap-5 sm:flex-row">
      <div class="relative h-44 w-44 shrink-0">
        <Doughnut :data="chartData" :options="chartOptions" />
        <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span class="text-2xl font-semibold text-slate-950 dark:text-white">{{ formatNumber(data.total) }}</span>
          <span class="text-xs text-slate-400">Total</span>
        </div>
      </div>
      <div class="w-full space-y-1.5">
        <div v-for="item in data.por_estado" :key="item.key" class="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-sm">
          <div class="flex min-w-0 items-center gap-2.5">
            <span class="h-2.5 w-2.5 shrink-0 rounded-full" :style="{ background: item.color }" />
            <span class="truncate font-medium text-slate-700 dark:text-slate-200">{{ item.label }}</span>
          </div>
          <span class="shrink-0 font-semibold text-slate-950 dark:text-white">{{ item.cantidad }}</span>
        </div>
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import BaseCard from '../BaseCard.vue'
import { useFormatters } from '../../composables/useFormatters'

const props = defineProps({
  data: { type: Object, required: true }, // { total, por_estado: [{key,label,color,cantidad}] }
})

const { formatNumber } = useFormatters()

const chartData = computed(() => ({
  labels: props.data.por_estado.map((item) => item.label),
  datasets: [
    {
      data: props.data.por_estado.map((item) => item.cantidad),
      backgroundColor: props.data.por_estado.map((item) => item.color),
      borderWidth: 0,
      hoverOffset: 8,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '72%',
  plugins: {
    legend: { display: false },
    tooltip: { backgroundColor: '#020617', padding: 12, cornerRadius: 10 },
  },
}
</script>
