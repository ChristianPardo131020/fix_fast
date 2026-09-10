<template>
  <BaseCard content-class="p-3.5 sm:p-4">
    <div class="flex flex-col gap-3 lg:flex-row lg:items-center">
      <span class="flex shrink-0 items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500">
        <AppIcon name="filter" class="h-3.5 w-3.5" /> {{ label }}
      </span>
      <div class="flex min-w-0 flex-1 flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
        <slot />
      </div>
    </div>
  </BaseCard>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import BaseCard from './BaseCard.vue'

// Barra de filtros a todo el ancho: agrupa los controles en un solo
// lugar (Ley de Región Común / Proximidad) y evita que se mezclen con
// los botones de acción del encabezado.
defineProps({
  label: { type: String, default: 'Filtros' },
})
</script>
