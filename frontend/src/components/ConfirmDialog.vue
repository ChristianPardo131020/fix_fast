<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="ui.confirmState" class="fixed inset-0 z-[70] flex items-end justify-center bg-slate-950/50 p-3 backdrop-blur-sm sm:items-center" @click.self="ui.resolveConfirm(false)">
        <div class="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-5 shadow-2xl dark:border-slate-800 dark:bg-slate-950">
          <div class="flex items-start gap-3">
            <div :class="toneClasses" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full">
              <AppIcon name="trash" class="h-5 w-5" />
            </div>
            <div class="min-w-0 pt-1">
              <h3 class="text-base font-semibold text-slate-950 dark:text-white">{{ ui.confirmState.title }}</h3>
              <p v-if="ui.confirmState.message" class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ ui.confirmState.message }}</p>
            </div>
          </div>
          <div class="mt-5 flex justify-end gap-2">
            <BaseButton variant="secondary" @click="ui.resolveConfirm(false)">{{ ui.confirmState.cancelLabel }}</BaseButton>
            <BaseButton :variant="ui.confirmState.tone === 'danger' ? 'danger' : 'primary'" @click="ui.resolveConfirm(true)">{{ ui.confirmState.confirmLabel }}</BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import BaseButton from './BaseButton.vue'
import { useUiStore } from '../stores/ui'

const ui = useUiStore()

const toneClasses = computed(() =>
  ui.confirmState?.tone === 'danger'
    ? 'bg-red-100 text-red-600 dark:bg-red-500/15 dark:text-red-300'
    : 'bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300',
)
</script>
