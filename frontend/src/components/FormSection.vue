<template>
  <section class="rounded-xl border border-slate-200 bg-slate-50/60 p-4 dark:border-slate-800 dark:bg-slate-900/40">
    <h3 v-if="label" class="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{{ label }}</h3>
    <div class="grid gap-4">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  label: { type: String, default: '' },
})
</script>
