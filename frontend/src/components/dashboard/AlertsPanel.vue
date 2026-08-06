<template>
  <BaseCard title="Alertas" subtitle="Se calculan solas, nada escrito a mano" content-class="p-4">
    <div v-if="alerts.length" class="space-y-2.5">
      <div
        v-for="alert in alerts"
        :key="alert.tipo"
        class="flex items-start gap-3 rounded-xl border p-3"
        :class="severityClasses[alert.severidad].border"
      >
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg" :class="severityClasses[alert.severidad].iconBg">
          <AppIcon name="alert" class="h-4 w-4" :class="severityClasses[alert.severidad].iconColor" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center justify-between gap-2">
            <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">{{ alert.titulo }}</p>
            <span v-if="alert.monto" class="shrink-0 text-sm font-semibold text-slate-950 dark:text-white">{{ formatCurrency(alert.monto) }}</span>
          </div>
          <p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{{ alert.mensaje }}</p>
        </div>
      </div>
    </div>
    <EmptyState v-else icon="check" title="Todo en orden" description="No hay alertas activas para este periodo." />
  </BaseCard>
</template>

<script setup>
import AppIcon from '../AppIcon.vue'
import BaseCard from '../BaseCard.vue'
import EmptyState from '../EmptyState.vue'
import { useFormatters } from '../../composables/useFormatters'

defineProps({
  alerts: { type: Array, required: true }, // [{tipo, severidad, titulo, mensaje, cantidad, monto}]
})

const { formatCurrency } = useFormatters()

const severityClasses = {
  alta: {
    border: 'border-red-200 bg-red-50/60 dark:border-red-500/20 dark:bg-red-500/5',
    iconBg: 'bg-red-100 dark:bg-red-500/15',
    iconColor: 'text-red-600 dark:text-red-400',
  },
  media: {
    border: 'border-orange-200 bg-orange-50/60 dark:border-orange-500/20 dark:bg-orange-500/5',
    iconBg: 'bg-orange-100 dark:bg-orange-500/15',
    iconColor: 'text-orange-600 dark:text-orange-400',
  },
  baja: {
    border: 'border-slate-200 bg-slate-50/60 dark:border-slate-800 dark:bg-slate-900/40',
    iconBg: 'bg-slate-100 dark:bg-slate-800',
    iconColor: 'text-slate-600 dark:text-slate-300',
  },
}
</script>
