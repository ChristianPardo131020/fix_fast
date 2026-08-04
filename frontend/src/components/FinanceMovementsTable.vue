<template>
  <BaseTable :columns="columns" :rows="rows" :loading="loading">
    <template #tipo="{ row }">
      <FinanceTypeBadge :value="row.tipo" />
    </template>
    <template #categoria="{ row }">
      <span class="capitalize">{{ row.categoria || 'otros' }}</span>
    </template>
    <template #valor="{ row }">
      <span :class="row.tipo === 'ingreso' ? 'text-emerald-700 dark:text-emerald-300' : 'text-rose-700 dark:text-rose-300'" class="font-semibold">
        {{ row.tipo === 'ingreso' ? '+' : '-' }} {{ formatCurrency(row.valor) }}
      </span>
    </template>
    <template #metodo_pago="{ row }">
      <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-slate-700 dark:bg-slate-800 dark:text-slate-200">
        {{ row.metodo_pago || 'sin metodo' }}
      </span>
    </template>
    <template #descripcion="{ row }">
      <span class="block max-w-[24rem] truncate">{{ row.descripcion || '-' }}</span>
    </template>
    <template #created_at="{ row }">
      {{ formatDate(row.created_at) }}
    </template>
    <template #empty>
      <EmptyState icon="cash" title="Sin movimientos" description="Registra ingresos o egresos para comenzar a visualizar tu flujo financiero." />
    </template>
    <template #actions="{ row }">
      <BaseButton variant="ghost" size="sm" icon="trash" @click="$emit('delete', row)">Eliminar</BaseButton>
    </template>
  </BaseTable>
</template>

<script setup>
import BaseButton from './BaseButton.vue'
import BaseTable from './BaseTable.vue'
import EmptyState from './EmptyState.vue'
import FinanceTypeBadge from './FinanceTypeBadge.vue'
import { useFormatters } from '../composables/useFormatters'

defineProps({
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

defineEmits(['delete'])

const { formatCurrency, formatDate } = useFormatters()
const columns = [
  { key: 'tipo', label: 'Tipo' },
  { key: 'categoria', label: 'Categoria' },
  { key: 'valor', label: 'Valor' },
  { key: 'metodo_pago', label: 'Metodo' },
  { key: 'descripcion', label: 'Descripcion' },
  { key: 'created_at', label: 'Fecha' },
]
</script>
