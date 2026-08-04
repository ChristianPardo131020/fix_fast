<template>
  <button
    type="button"
    class="fixed bottom-20 right-4 z-20 flex h-14 w-14 items-center justify-center rounded-full bg-slate-950 text-white shadow-lift transition hover:-translate-y-0.5 active:translate-y-0 lg:hidden dark:bg-white dark:text-slate-950"
    :aria-label="label"
    @click="$emit('click')"
  >
    <AppIcon name="plus" class="h-6 w-6" />
  </button>
</template>

<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  label: { type: String, default: 'Crear' },
})
defineEmits(['click'])
</script>
