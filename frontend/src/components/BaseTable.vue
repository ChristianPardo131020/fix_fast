<template>
  <div>
    <!-- Mobile: lista de tarjetas -->
    <div class="space-y-3 sm:hidden">
      <div v-if="loading" class="space-y-3">
        <div v-for="n in 3" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
          <div v-for="c in columns.length" :key="c" class="mb-2.5 flex items-center justify-between gap-3 last:mb-0">
            <span class="h-3 w-16 rounded bg-slate-200 dark:bg-slate-800" />
            <span class="h-3 w-24 rounded bg-slate-200 dark:bg-slate-800" />
          </div>
        </div>
      </div>
      <div v-else-if="!rows.length" class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900">
        <slot name="empty">
          <p class="text-center text-sm text-slate-500">No hay registros para mostrar.</p>
        </slot>
      </div>
      <div
        v-else
        v-for="row in rows"
        :key="row.id || row._key"
        class="rounded-xl border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900"
      >
        <dl class="space-y-2.5">
          <div v-for="column in columns" :key="column.key" class="flex items-start justify-between gap-3 text-sm">
            <dt class="shrink-0 pt-0.5 text-xs font-medium uppercase tracking-wide text-slate-400">{{ column.label }}</dt>
            <dd class="min-w-0 text-right text-slate-700 dark:text-slate-200">
              <slot :name="column.key" :row="row" :value="row[column.key]">{{ row[column.key] ?? '-' }}</slot>
            </dd>
          </div>
        </dl>
        <div v-if="$slots.actions" class="mt-3 flex flex-wrap justify-end gap-2 border-t border-slate-100 pt-3 dark:border-slate-800">
          <slot name="actions" :row="row" />
        </div>
      </div>
    </div>

    <!-- Desktop / tablet: tabla -->
    <div class="hidden overflow-hidden rounded-xl border border-slate-200 bg-white sm:block dark:border-slate-800 dark:bg-slate-900">
      <div class="overflow-x-auto scrollbar-thin">
        <table class="min-w-full divide-y divide-slate-100 text-left text-sm dark:divide-slate-800">
          <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500 dark:bg-slate-900/80 dark:text-slate-400">
            <tr>
              <th v-for="column in columns" :key="column.key" class="whitespace-nowrap px-4 py-3 font-semibold">{{ column.label }}</th>
              <th v-if="$slots.actions" class="px-4 py-3 text-right font-semibold">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <template v-if="loading">
              <tr v-for="n in 5" :key="`skeleton-${n}`" class="animate-pulse">
                <td v-for="column in columns" :key="column.key" class="px-4 py-3.5">
                  <span class="block h-3 w-full max-w-[10rem] rounded bg-slate-200 dark:bg-slate-800" />
                </td>
                <td v-if="$slots.actions" class="px-4 py-3.5 text-right">
                  <span class="ml-auto block h-3 w-16 rounded bg-slate-200 dark:bg-slate-800" />
                </td>
              </tr>
            </template>
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
  </div>
</template>

<script setup>
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})
</script>
