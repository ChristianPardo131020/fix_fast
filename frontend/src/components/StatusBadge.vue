<template>
  <span :class="tone.classes" class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold">
    <span :class="tone.dot" class="h-1.5 w-1.5 rounded-full" />
    {{ estado.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { resolveEstado } from '../constants/estados'

const props = defineProps({
  value: { type: String, default: '' },
})

const estado = computed(() => resolveEstado(props.value))

// Clases Tailwind (con variante dark) por key canonica. La logica de
// "que estado es este string" vive una sola vez en resolveEstado
// (constants/estados.js); esto solo mapea la key resultante a color de
// UI, que es puramente de presentacion.
const tones = {
  pendiente: { classes: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300', dot: 'bg-slate-500' },
  diagnostico: { classes: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300', dot: 'bg-sky-500' },
  esperando_repuesto: { classes: 'bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300', dot: 'bg-orange-500' },
  reparacion: { classes: 'bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300', dot: 'bg-brand-500' },
  listo: { classes: 'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300', dot: 'bg-green-500' },
  entregado: { classes: 'bg-purple-100 text-purple-700 dark:bg-purple-500/15 dark:text-purple-300', dot: 'bg-purple-500' },
  cancelado: { classes: 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300', dot: 'bg-red-500' },
}

const tone = computed(() => tones[estado.value.key])
</script>
