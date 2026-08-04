import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { supabase } from '../lib/supabaseClient'
import { meRequest } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const session = ref(null)
  const loading = ref(false)
  const user = ref(null)

  const isAuthenticated = computed(() => Boolean(session.value))
  const token = computed(() => session.value?.access_token ?? null)

  // Hidrata la sesión ya persistida por supabase-js (localStorage) y se
  // suscribe a cambios (login, logout, refresh de token). Se llama antes
  // de montar la app para que el guard de router no redirija mal en un
  // hard-refresh de una ruta protegida.
  async function init() {
    const { data } = await supabase.auth.getSession()
    session.value = data.session

    supabase.auth.onAuthStateChange((_event, newSession) => {
      session.value = newSession
    })

    if (session.value) {
      await fetchProfile()
    }
  }

  async function fetchProfile() {
    try {
      const response = await meRequest()
      user.value = {
        name: response.data.nombre,
        role: response.data.rol,
        email: response.data.email,
      }
    } catch {
      user.value = null
    }
  }

  async function login(credentials) {
    loading.value = true

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: credentials.email,
        password: credentials.password,
      })

      if (error) throw error

      session.value = data.session
      await fetchProfile()
      return data
    } finally {
      loading.value = false
    }
  }

  function logout(redirect = true) {
    supabase.auth.signOut()
    session.value = null
    user.value = null

    if (redirect) {
      window.location.assign('/login')
    }
  }

  return { session, token, user, loading, isAuthenticated, login, logout, init }
})
