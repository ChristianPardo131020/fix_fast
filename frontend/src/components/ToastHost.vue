<template>
  <div class="fixed right-4 top-4 z-[60] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-3">
    <TransitionGroup name="toast">
      <div
        v-for="toast in ui.toasts"
        :key="toast.id"
        :class="toast.type === 'error'
          ? 'border-red-200 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200'
          : 'border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200'"
        class="flex items-start gap-3 rounded-xl border px-4 py-3 text-sm shadow-lg backdrop-blur"
      >
        <div
          class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full"
          :class="toast.type === 'error' ? 'bg-red-100 dark:bg-red-900/40' : 'bg-emerald-100 dark:bg-emerald-900/40'"
        >
          <AppIcon :name="toast.type === 'error' ? 'alert' : 'check'" class="h-4 w-4" />
        </div>
        <span class="min-w-0 flex-1 leading-snug">{{ toast.message }}</span>
        <button type="button" class="shrink-0 rounded p-0.5 opacity-60 transition hover:opacity-100" title="Cerrar" @click="ui.dismissToast(toast.id)">
          <AppIcon name="x" class="h-4 w-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import { useUiStore } from '../stores/ui'

const ui = useUiStore()
</script>
