<template>
  <div class="relative">
    <select
      :value="modelValue"
      :required="required"
      :disabled="disabled"
      class="h-10 w-full appearance-none rounded-lg border pr-9 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500 dark:text-slate-200 dark:disabled:bg-slate-900 dark:disabled:text-slate-400"
      :class="variantClasses"
      @change="onChange"
    >
      <slot />
    </select>
    <AppIcon name="chevron-down" class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  // 'toolbar': sobre el fondo de página (header). 'card': dentro de una tarjeta.
  variant: { type: String, default: 'toolbar' },
})

const emit = defineEmits(['update:modelValue'])

const variantClasses = computed(() =>
  props.variant === 'card'
    ? 'border-slate-200 bg-white pl-3 dark:border-slate-800 dark:bg-slate-950'
    : 'border-slate-200 bg-white pl-3 dark:border-slate-800 dark:bg-slate-900',
)

function onChange(event) {
  const select = event.target
  const option = select.options[select.selectedIndex]
  // Replica el tipado del v-model nativo: un <option :value="null"> o
  // :value="3" conserva su tipo (null/number) en lugar de volverse string.
  const value = option?._value !== undefined ? option._value : event.target.value
  emit('update:modelValue', value)
}
</script>
