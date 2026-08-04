<template>
  <BaseCard content-class="p-5">
    <div class="flex items-start justify-between gap-4">
      <div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ label }}</p>
        <p class="mt-2 text-2xl font-semibold text-slate-950 dark:text-white">{{ value }}</p>
      </div>
      <div :class="toneClass" class="flex h-10 w-10 items-center justify-center rounded-lg">
        <AppIcon :name="icon" />
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
})

const toneClass = computed(() => ({
  teal: 'bg-teal-100 text-teal-700 dark:bg-teal-500/15 dark:text-teal-300',
  slate: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300',
  rose: 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300',
  sky: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300',
}[props.tone]))
</script>
