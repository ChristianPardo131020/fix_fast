<template>
  <div class="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 px-6 py-10 text-center dark:border-slate-800">
    <div class="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 text-slate-500 shadow-inner ring-1 ring-slate-200/60 dark:from-slate-800 dark:to-slate-800/50 dark:text-slate-300 dark:ring-slate-700/60">
      <AppIcon :name="icon" class="h-6 w-6" />
    </div>
    <h3 class="text-sm font-semibold text-slate-900 dark:text-white">{{ title }}</h3>
    <p class="mt-1 max-w-md text-sm text-slate-500 dark:text-slate-400">{{ description }}</p>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  icon: { type: String, default: 'dashboard' },
  title: { type: String, default: 'Sin datos' },
  description: { type: String, default: 'Cuando existan registros apareceran aqui.' },
})
</script>
