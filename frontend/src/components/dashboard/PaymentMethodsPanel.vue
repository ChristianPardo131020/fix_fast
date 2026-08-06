<template>
  <BaseCard title="Metodos de pago" subtitle="Como entro el dinero en el periodo">
    <div v-if="data.por_metodo.length" class="space-y-4">
      <div v-for="item in data.por_metodo" :key="item.metodo">
        <div class="mb-1.5 flex items-center justify-between gap-3 text-sm">
          <span class="font-medium text-slate-700 dark:text-slate-200">{{ item.metodo }}</span>
          <span class="text-slate-500 dark:text-slate-400">{{ formatCurrency(item.monto) }} · {{ item.cantidad }}</span>
        </div>
        <div class="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
          <div class="h-full rounded-full bg-brand-500 transition-all" :style="{ width: `${percentOf(item.monto)}%` }" />
        </div>
      </div>
    </div>
    <EmptyState v-else icon="payments" title="Sin pagos en el periodo" description="Los metodos de pago apareceran cuando registres pagos o ingresos." />
  </BaseCard>
</template>

<script setup>
import BaseCard from '../BaseCard.vue'
import EmptyState from '../EmptyState.vue'
import { useFormatters } from '../../composables/useFormatters'

const props = defineProps({
  data: { type: Object, required: true }, // { total_monto, por_metodo: [{metodo, cantidad, monto}] }
})

const { formatCurrency } = useFormatters()

function percentOf(monto) {
  if (!Number(props.data.total_monto)) return 0
  return Math.max((Number(monto) / Number(props.data.total_monto)) * 100, 4)
}
</script>
