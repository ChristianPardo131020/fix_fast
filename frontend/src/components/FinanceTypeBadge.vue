<template>
  <span :class="classes" class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold capitalize">
    {{ value || 'sin tipo' }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: String, default: '' },
})

const classes = computed(() => {
  if (props.value === 'ingreso') {
    return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300'
  }

  if (props.value === 'egreso') {
    return 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300'
  }

  return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
})
</script>
