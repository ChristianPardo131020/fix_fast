import axios from 'axios'
import router from '../router'
import { useAuthStore } from '../stores/auth'

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('fixfast_token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout(false)
      router.push({ name: 'login' })
    }

    return Promise.reject(error)
  },
)

export default http
