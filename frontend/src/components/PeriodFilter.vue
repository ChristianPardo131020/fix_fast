<template>
  <div class="flex flex-wrap items-center gap-2">
    <button
      v-for="preset in presets"
      :key="preset.key"
      type="button"
      class="rounded-full border px-3 py-1.5 text-xs font-medium transition"
      :class="isActive(preset)
        ? 'border-brand-500 bg-brand-50 text-brand-700 dark:border-brand-500 dark:bg-brand-500/10 dark:text-brand-300'
        : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-800 dark:text-slate-300 dark:hover:bg-slate-900'"
      @click="apply(preset)"
    >
      {{ preset.label }}
    </button>

    <div class="flex items-center gap-1.5">
      <input
        type="date"
        :value="modelValue.desde"
        :max="modelValue.hasta || undefined"
        class="h-8 rounded-lg border border-slate-200 bg-white px-2 text-xs text-slate-700 outline-none focus:border-brand-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200"
        @input="setRange({ desde: $event.target.value, hasta: modelValue.hasta })"
      />
      <span class="text-xs text-slate-400">a</span>
      <input
        type="date"
        :value="modelValue.hasta"
        :min="modelValue.desde || undefined"
        class="h-8 rounded-lg border border-slate-200 bg-white px-2 text-xs text-slate-700 outline-none focus:border-brand-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200"
        @input="setRange({ desde: modelValue.desde, hasta: $event.target.value })"
      />
    </div>
  </div>
</template>

<script setup>
// Filtro de periodo reutilizable (Ingresos, Egresos): unos presets
// comunes para segmentar rapido, mas un rango Desde/Hasta libre para
// cualquier otro caso (ej. un mes cerrado especifico). El filtrado en
// si lo hace cada vista sobre sus propias filas -- este componente solo
// entrega { desde, hasta } en formato YYYY-MM-DD.
import { computed } from 'vue'
import { rangoEsteAnio, rangoEsteMes, rangoEstaSemana, rangoHoy } from '../utils/dateRanges'

const props = defineProps({
  modelValue: { type: Object, required: true }, // { desde: 'YYYY-MM-DD'|'', hasta: 'YYYY-MM-DD'|'' }
})

const emit = defineEmits(['update:modelValue'])

const presets = computed(() => [
  { key: 'hoy', label: 'Hoy', range: rangoHoy },
  { key: 'semana', label: 'Esta semana', range: rangoEstaSemana },
  { key: 'mes', label: 'Este mes', range: rangoEsteMes },
  { key: 'anio', label: 'Este año', range: rangoEsteAnio },
  { key: 'todo', label: 'Todo', range: () => ({ desde: '', hasta: '' }) },
])

function isActive(preset) {
  const range = preset.range()
  return range.desde === (props.modelValue.desde || '') && range.hasta === (props.modelValue.hasta || '')
}

function apply(preset) {
  setRange(preset.range())
}

function setRange(range) {
  emit('update:modelValue', range)
}
</script>
