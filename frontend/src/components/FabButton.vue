<template>
  <button
    type="button"
    class="fixed bottom-20 right-4 z-20 flex h-14 w-14 items-center justify-center rounded-full bg-brand-600 text-white shadow-lift transition hover:-translate-y-0.5 hover:bg-brand-700 active:translate-y-0 lg:hidden"
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
