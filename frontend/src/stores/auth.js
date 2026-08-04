import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { loginRequest } from '../api/auth'

const TOKEN_KEY = 'fixfast_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY))
  const loading = ref(false)
  const user = ref({ name: 'Administrador', role: 'Operaciones' })

  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(credentials) {
    loading.value = true

    try {
      const payload = new URLSearchParams()
      payload.append('username', credentials.email)
      payload.append('password', credentials.password)

      let response

      try {
        response = await loginRequest(payload, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
      } catch (formError) {
        response = await loginRequest({
          username: credentials.email,
          email: credentials.email,
          password: credentials.password,
        })
      }

      token.value = response.data.access_token
      localStorage.setItem(TOKEN_KEY, token.value)
      return response.data
    } finally {
      loading.value = false
    }
  }

  function logout(redirect = true) {
    token.value = null
    localStorage.removeItem(TOKEN_KEY)

    if (redirect) {
      window.location.assign('/login')
    }
  }

  return { token, user, loading, isAuthenticated, login, logout }
})
