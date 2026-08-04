import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const auth = useAuthStore()

// Espera a que la sesión de Supabase se hidrate antes de montar: si no,
// el guard de router puede correr con isAuthenticated en falso durante un
// hard-refresh de una ruta protegida y redirigir mal a /login.
auth.init().finally(() => {
  app.mount('#app')
})
