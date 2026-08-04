<template>
  <BaseCard content-class="p-5" class="transition hover:-translate-y-0.5 hover:shadow-lift">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0">
        <p class="truncate text-sm font-medium text-slate-500 dark:text-slate-400">{{ label }}</p>
        <p class="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">{{ value }}</p>
      </div>
      <div :class="toneClass" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl">
        <AppIcon :name="icon" class="h-5 w-5" />
      </div>
    </div>

    <div v-if="trend || spark.length" class="mt-4 flex items-end justify-between gap-3">
      <span v-if="trend" class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">{{ trend }}</span>
      <div v-if="spark.length" class="flex h-8 items-end gap-1">
        <span v-for="(item, index) in spark" :key="index" class="w-1.5 rounded-full bg-slate-300 dark:bg-slate-700" :style="{ height: `${item}%` }" />
      </div>
    </div>

    <p v-if="hint" class="mt-4 text-xs text-slate-500 dark:text-slate-400">{{ hint }}</p>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import BaseCard from './BaseCard.vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  icon: { type: String, default: 'dashboard' },
  tone: { type: String, default: 'teal' },
  hint: { type: String, default: '' },
  trend: { type: String, default: '' },
  spark: { type: Array, default: () => [] },
})

const toneClass = computed(() => ({
  teal: 'bg-teal-100 text-teal-700 dark:bg-teal-500/15 dark:text-teal-300',
  slate: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300',
  rose: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
  sky: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300',
  brand: 'bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300',
  green: 'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300',
  orange: 'bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300',
  purple: 'bg-purple-100 text-purple-700 dark:bg-purple-500/15 dark:text-purple-300',
}[props.tone]))
</script>
