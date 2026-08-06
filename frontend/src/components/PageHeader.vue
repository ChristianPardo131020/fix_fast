<template>
  <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
    <div class="min-w-0">
      <div v-if="$slots.eyebrow" class="mb-2 flex flex-wrap items-center gap-2">
        <slot name="eyebrow" />
      </div>
      <h1 class="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl dark:text-white">{{ title }}</h1>
      <p v-if="subtitle || $slots.default" class="mt-1.5 max-w-2xl text-sm text-slate-500 dark:text-slate-400">
        <slot>{{ subtitle }}</slot>
      </p>
    </div>
    <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>
