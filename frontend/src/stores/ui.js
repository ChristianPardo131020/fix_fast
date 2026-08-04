import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', () => {
  const sidebarOpen = ref(false)
  const sidebarCollapsed = ref(localStorage.getItem('fixfast_sidebar_collapsed') === '1')
  const darkMode = ref(localStorage.getItem('fixfast_theme') === 'dark')
  const toasts = ref([])

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

  return {
    sidebarOpen,
    sidebarCollapsed,
    darkMode,
    toasts,
    toggleSidebar,
    closeSidebar,
    toggleSidebarCollapsed,
    toggleTheme,
    hydrateTheme,
    toast,
    dismissToast,
  }
})
