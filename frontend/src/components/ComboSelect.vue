<template>
  <label class="relative block" ref="rootRef">
    <span v-if="label" class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-200">{{ label }}<span v-if="required" class="text-rose-500"> *</span></span>

    <div class="relative">
      <input
        type="text"
        class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-16 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-white"
        :placeholder="placeholder"
        :required="required && !modelValue"
        :value="open ? query : (selectedOption?.label || '')"
        @focus="onFocus"
        @input="onInput"
        @keydown.down.prevent="moveHighlight(1)"
        @keydown.up.prevent="moveHighlight(-1)"
        @keydown.enter.prevent="selectHighlighted"
        @keydown.escape="close"
        @blur="onBlur"
      />
      <button
        v-if="modelValue"
        type="button"
        tabindex="-1"
        class="absolute right-7 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
        title="Limpiar"
        @mousedown.prevent="clear"
      >
        <AppIcon name="x" class="h-4 w-4" />
      </button>
      <AppIcon name="chevron-down" class="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
    </div>

    <div
      v-if="open"
      class="absolute z-30 mt-1 max-h-64 w-full overflow-y-auto rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-800 dark:bg-slate-900"
    >
      <button
        v-for="(opt, idx) in filteredOptions"
        :key="opt.value"
        type="button"
        class="flex w-full flex-col px-3 py-2 text-left text-sm"
        :class="idx === highlighted ? 'bg-brand-50 dark:bg-brand-500/10' : 'hover:bg-slate-100 dark:hover:bg-slate-800'"
        @mousedown.prevent="select(opt)"
      >
        <span class="truncate font-medium text-slate-900 dark:text-slate-100">{{ opt.label }}</span>
        <span v-if="opt.sublabel" class="truncate text-xs text-slate-500 dark:text-slate-400">{{ opt.sublabel }}</span>
      </button>
      <p v-if="!filteredOptions.length" class="px-3 py-2 text-sm text-slate-500 dark:text-slate-400">
        Sin resultados{{ query ? ` para "${query}"` : '' }}
      </p>
      <p v-else-if="hasMore" class="px-3 py-1.5 text-xs text-slate-400 dark:text-slate-500">
        Seguí escribiendo para filtrar ({{ options.length }} en total)
      </p>
    </div>
  </label>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from './AppIcon.vue'

// Combobox con filtro en el propio navegador para listas grandes
// (clientes, ordenes: miles de filas). Un <select> nativo con miles de
// <option> tarda en abrir/renderizar y se traba al buscar; acá solo se
// renderizan los primeros MAX_RESULTS que matchean lo tipeado.
const MAX_RESULTS = 50

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  options: { type: Array, default: () => [] }, // [{ value, label, sublabel? }]
  label: { type: String, default: '' },
  placeholder: { type: String, default: 'Buscar...' },
  required: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const rootRef = ref(null)
const query = ref('')
const open = ref(false)
const highlighted = ref(0)

const selectedOption = computed(() =>
  props.options.find((opt) => String(opt.value) === String(props.modelValue)) || null,
)

const filteredOptions = computed(() => {
  const term = query.value.toLowerCase().trim()
  if (!term) return props.options.slice(0, MAX_RESULTS)

  const matches = []
  for (const opt of props.options) {
    if (opt.label?.toLowerCase().includes(term) || opt.sublabel?.toLowerCase().includes(term)) {
      matches.push(opt)
      if (matches.length >= MAX_RESULTS) break
    }
  }
  return matches
})

const hasMore = computed(() => filteredOptions.value.length >= MAX_RESULTS)

function onFocus() {
  query.value = ''
  open.value = true
  highlighted.value = 0
}

function onInput(event) {
  query.value = event.target.value
  open.value = true
  highlighted.value = 0
}

function select(opt) {
  emit('update:modelValue', opt.value)
  query.value = opt.label
  close()
}

function clear() {
  emit('update:modelValue', '')
  query.value = ''
}

function close() {
  open.value = false
}

function onBlur() {
  // Se cierra en el próximo tick: los botones de opción usan
  // @mousedown.prevent (no roban el foco), así que un click en una
  // opción ya corrió select() antes de que esto se ejecute.
  close()
}

function moveHighlight(delta) {
  if (!open.value) {
    open.value = true
    return
  }
  const max = filteredOptions.value.length - 1
  if (max < 0) return
  highlighted.value = Math.min(max, Math.max(0, highlighted.value + delta))
}

function selectHighlighted() {
  const opt = filteredOptions.value[highlighted.value]
  if (opt) select(opt)
}

watch(filteredOptions, () => {
  if (highlighted.value > filteredOptions.value.length - 1) highlighted.value = 0
})

function onDocClick(event) {
  if (open.value && rootRef.value && !rootRef.value.contains(event.target)) {
    close()
  }
}

onMounted(() => document.addEventListener('mousedown', onDocClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))
</script>
