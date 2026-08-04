<template>
  <div class="overflow-hidden rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
    <div class="overflow-x-auto scrollbar-thin">
      <table class="min-w-full divide-y divide-slate-100 text-left text-sm dark:divide-slate-800">
        <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:bg-slate-900/80 dark:text-slate-400">
          <tr>
            <th v-for="column in columns" :key="column.key" class="whitespace-nowrap px-4 py-3 font-semibold">{{ column.label }}</th>
            <th v-if="$slots.actions" class="px-4 py-3 text-right font-semibold">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
          <tr v-if="loading">
            <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="px-4 py-8 text-center text-slate-500">
              <span class="mx-auto mb-3 block h-6 w-6 animate-spin rounded-full border-2 border-teal-600 border-t-transparent" />
              Cargando informacion...
            </td>
          </tr>
          <tr v-else-if="!rows.length">
            <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="px-4 py-10">
              <slot name="empty">
                <p class="text-center text-sm text-slate-500">No hay registros para mostrar.</p>
              </slot>
            </td>
          </tr>
          <tr v-for="row in rows" v-else :key="row.id || row._key" class="transition hover:bg-slate-50/80 dark:hover:bg-slate-800/50">
            <td v-for="column in columns" :key="column.key" class="whitespace-nowrap px-4 py-3 text-slate-700 dark:text-slate-200">
              <slot :name="column.key" :row="row" :value="row[column.key]">
                {{ row[column.key] ?? '-' }}
              </slot>
            </td>
            <td v-if="$slots.actions" class="whitespace-nowrap px-4 py-3 text-right">
              <slot name="actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})
</script>
