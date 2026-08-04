<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-end justify-center bg-slate-950/50 p-3 backdrop-blur-sm sm:items-center" @click.self="$emit('update:modelValue', false)">
        <div class="max-h-[92vh] w-full max-w-2xl overflow-hidden rounded-xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-950">
          <header class="flex items-start justify-between gap-4 border-b border-slate-100 px-5 py-4 dark:border-slate-800">
            <div>
              <h2 class="text-lg font-semibold text-slate-950 dark:text-white">{{ title }}</h2>
              <p v-if="subtitle" class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ subtitle }}</p>
            </div>
            <button class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" type="button" @click="$emit('update:modelValue', false)">x</button>
          </header>
          <div class="max-h-[calc(92vh-80px)] overflow-y-auto p-5 scrollbar-thin">
            <slot />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
})

defineEmits(['update:modelValue'])
</script>
