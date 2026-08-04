<template>
  <section class="rounded-xl border border-slate-200 bg-white/90 shadow-sm shadow-slate-200/70 backdrop-blur dark:border-slate-800 dark:bg-slate-900/90 dark:shadow-black/20">
    <div v-if="$slots.header || title" class="flex flex-col gap-3 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between dark:border-slate-800">
      <div>
        <h2 v-if="title" class="text-base font-semibold text-slate-950 dark:text-white">{{ title }}</h2>
        <p v-if="subtitle" class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ subtitle }}</p>
      </div>
      <slot name="header" />
    </div>
    <div :class="contentClass">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  contentClass: { type: String, default: 'p-5' },
})
</script>
