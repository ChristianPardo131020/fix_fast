<template>
  <span :class="classes" class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold">
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: String, default: '' },
})

const label = computed(() => props.value || 'Sin estado')

const classes = computed(() => {
  const state = props.value?.toLowerCase() || ''

  if (state.includes('entreg')) return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300'
  if (state.includes('pend') || state.includes('act')) return 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300'
  if (state.includes('cancel')) return 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300'
  if (state.includes('repar') || state.includes('proceso')) return 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300'

  return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
})
</script>
