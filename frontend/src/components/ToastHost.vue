<template>
  <div class="fixed right-4 top-4 z-[60] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-3">
    <TransitionGroup name="fade">
      <div
        v-for="toast in ui.toasts"
        :key="toast.id"
        :class="toast.type === 'error' ? 'border-red-200 bg-red-50 text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200' : 'border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-200'"
        class="rounded-xl border px-4 py-3 text-sm shadow-lg"
      >
        <div class="flex items-start justify-between gap-3">
          <span>{{ toast.message }}</span>
          <button type="button" class="font-semibold opacity-70 hover:opacity-100" @click="ui.dismissToast(toast.id)">x</button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useUiStore } from '../stores/ui'

const ui = useUiStore()
</script>
