<template>
  <BaseCard content-class="p-4">
    <!-- Caso terminal: orden cancelada -->
    <div v-if="cancelado" class="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-500/20 dark:bg-red-500/5">
      <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-red-100 dark:bg-red-500/15">
        <AppIcon name="alert" class="h-4 w-4 text-red-600 dark:text-red-400" />
      </span>
      <div class="min-w-0">
        <p class="text-sm font-semibold text-red-700 dark:text-red-300">Orden cancelada</p>
        <p class="text-xs text-red-600/80 dark:text-red-300/70">Esta reparación ya no está en curso.</p>
      </div>
    </div>

    <!-- Flujo normal: Pendiente → Listo → Entregado -->
    <ol v-else class="flex items-start">
      <li v-for="(step, i) in steps" :key="step.key" class="flex flex-1 items-start last:flex-none">
        <div class="flex flex-col items-center">
          <span :class="dotClass(i)" class="flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold transition-colors">
            <AppIcon v-if="i < activeIndex" name="check" class="h-3.5 w-3.5" />
            <span v-else>{{ i + 1 }}</span>
          </span>
          <span :class="labelClass(i)" class="mt-1.5 whitespace-nowrap text-xs font-medium">{{ step.label }}</span>
        </div>
        <span v-if="i < steps.length - 1" class="mx-2 mt-[13px] h-0.5 flex-1 rounded-full transition-colors" :class="lineClass(i)" />
      </li>
    </ol>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import BaseCard from './BaseCard.vue'
import { resolveEstado } from '../constants/estados'

const props = defineProps({
  estado: { type: String, default: '' },
})

// Flujo canónico del taller: los 3 hitos visibles para el cliente.
const steps = [
  { key: 'pendiente', label: 'Pendiente' },
  { key: 'listo', label: 'Listo' },
  { key: 'entregado', label: 'Entregado' },
]

const estadoKey = computed(() => resolveEstado(props.estado).key)
const cancelado = computed(() => estadoKey.value === 'cancelado')

// entregado_sr (sin recibo) cuenta como entregado a efectos del flujo.
const activeIndex = computed(() => {
  if (estadoKey.value === 'entregado_sr') return 2
  return Math.max(steps.findIndex((s) => s.key === estadoKey.value), 0)
})

function dotClass(i) {
  if (i < activeIndex.value) return 'bg-green-500 text-white'
  if (i === activeIndex.value) return 'bg-brand-600 text-white ring-4 ring-brand-500/20'
  return 'bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500'
}

function labelClass(i) {
  if (i < activeIndex.value) return 'text-green-600 dark:text-green-400'
  if (i === activeIndex.value) return 'font-semibold text-brand-700 dark:text-brand-300'
  return 'text-slate-400 dark:text-slate-500'
}

function lineClass(i) {
  return i < activeIndex.value ? 'bg-green-500' : 'bg-slate-200 dark:bg-slate-700'
}
</script>
