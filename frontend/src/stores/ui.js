import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', () => {
  const sidebarOpen = ref(false)
  const sidebarCollapsed = ref(localStorage.getItem('fixfast_sidebar_collapsed') === '1')
  const darkMode = ref(localStorage.getItem('fixfast_theme') === 'dark')
  const toasts = ref([])
  const confirmState = ref(null)

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function closeSidebar() {
    sidebarOpen.value = false
  }

  function toggleSidebarCollapsed() {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('fixfast_sidebar_collapsed', sidebarCollapsed.value ? '1' : '0')
  }

  function toggleTheme() {
    darkMode.value = !darkMode.value
    localStorage.setItem('fixfast_theme', darkMode.value ? 'dark' : 'light')
    document.documentElement.classList.toggle('dark', darkMode.value)
  }

  function hydrateTheme() {
    document.documentElement.classList.toggle('dark', darkMode.value)
  }

  function toast(message, type = 'success') {
    const id = crypto.randomUUID()
    toasts.value.push({ id, message, type })
    window.setTimeout(() => dismissToast(id), 3800)
  }

  function dismissToast(id) {
    toasts.value = toasts.value.filter((item) => item.id !== id)
  }

  // Reemplazo del confirm() nativo del navegador: cualquier vista puede hacer
  // `await ui.confirm({ title, message })` y obtiene una Promise<boolean>,
  // resuelta cuando el usuario confirma o cancela en ConfirmDialog.vue.
  function confirm({ title = 'Confirmar accion', message = '', confirmLabel = 'Eliminar', cancelLabel = 'Cancelar', tone = 'danger' } = {}) {
    return new Promise((resolve) => {
      confirmState.value = { title, message, confirmLabel, cancelLabel, tone, resolve }
    })
  }

  function resolveConfirm(value) {
    confirmState.value?.resolve(value)
    confirmState.value = null
  }

  return {
    sidebarOpen,
    sidebarCollapsed,
    darkMode,
    toasts,
    confirmState,
    toggleSidebar,
    closeSidebar,
    toggleSidebarCollapsed,
    toggleTheme,
    hydrateTheme,
    toast,
    dismissToast,
    confirm,
    resolveConfirm,
  }
})
