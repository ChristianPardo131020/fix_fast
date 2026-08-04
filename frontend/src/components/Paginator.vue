<template>
  <div v-if="totalPages > 1" class="mt-4 flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between dark:border-slate-800">
    <p class="text-sm text-slate-500 dark:text-slate-400">
      Pagina {{ page }} de {{ totalPages }} · {{ formatNumber(totalItems) }} en total
    </p>
    <div class="flex items-center gap-2">
      <BaseButton variant="secondary" size="sm" icon="chevron-left" :disabled="page <= 1" @click="$emit('update:page', page - 1)">
        Anterior
      </BaseButton>
      <BaseButton variant="secondary" size="sm" :disabled="page >= totalPages" @click="$emit('update:page', page + 1)">
        Siguiente
        <AppIcon name="chevron-right" class="h-4 w-4" />
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import BaseButton from './BaseButton.vue'
import { useFormatters } from '../composables/useFormatters'

defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
  totalItems: { type: Number, required: true },
})
defineEmits(['update:page'])

const { formatNumber } = useFormatters()
</script>
