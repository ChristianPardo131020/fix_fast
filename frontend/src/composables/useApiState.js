import { ref } from 'vue'
import { useUiStore } from '../stores/ui'

export function useApiState() {
  const loading = ref(false)
  const error = ref('')
  const ui = useUiStore()

  async function run(action, successMessage = '') {
    loading.value = true
    error.value = ''

    try {
      const result = await action()

      if (successMessage) {
        ui.toast(successMessage)
      }

      return result
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'No se pudo completar la accion'
      error.value = Array.isArray(message) ? message[0]?.msg : message
      ui.toast(error.value, 'error')
      throw err
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run }
}
