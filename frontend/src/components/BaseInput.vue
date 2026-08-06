<template>
  <label class="block">
    <span v-if="label" class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-200">{{ label }}</span>
    <textarea
      v-if="textarea"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      rows="4"
      class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-white"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <select
      v-else-if="type === 'select'"
      :value="modelValue"
      :required="required"
      class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-white"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <slot />
    </select>
    <input
      v-else
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-white dark:disabled:bg-slate-900 dark:disabled:text-slate-400"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <p v-if="hint" class="mt-1.5 text-xs text-slate-500 dark:text-slate-400">{{ hint }}</p>
  </label>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  type: { type: String, default: 'text' },
  required: { type: Boolean, default: false },
  textarea: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  hint: { type: String, default: '' },
})

defineEmits(['update:modelValue'])
</script>
