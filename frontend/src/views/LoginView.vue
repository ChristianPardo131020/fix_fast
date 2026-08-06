<template>
  <main class="grid min-h-screen bg-slate-950 text-white lg:grid-cols-[1.05fr_0.95fr]">
    <section class="hidden flex-col justify-between bg-slate-950 p-10 lg:flex">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white p-1 shadow-sm">
          <img src="/logo-mark.png" alt="FixFast" class="h-full w-full object-contain" />
        </div>
        <div>
          <p class="font-semibold">FixFast</p>
          <p class="text-sm text-slate-400">Panel del equipo del taller</p>
        </div>
      </div>

      <div class="max-w-xl">
        <p class="mb-4 inline-flex rounded-full border border-white/10 px-3 py-1 text-sm text-brand-200">Operaciones, caja y reparaciones en un solo lugar</p>
        <h1 class="text-5xl font-semibold leading-tight">Que bueno verte de nuevo.</h1>
        <p class="mt-5 text-lg text-slate-300">Ingresa con tu cuenta de administrador para gestionar ordenes, clientes, pagos y caja del taller.</p>
      </div>

      <div class="rounded-xl border border-white/10 bg-white/[0.04] p-4">
        <p class="text-sm font-medium text-white">¿Buscas el estado de una reparacion?</p>
        <p class="mt-1 text-sm text-slate-400">Este acceso es solo para el equipo del taller. Si sos cliente y queres saber en que va tu equipo, no necesitas cuenta.</p>
        <RouterLink :to="{ name: 'seguimiento' }" class="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-brand-300 hover:text-brand-200">
          Consultar estado de mi reparacion
          <AppIcon name="chevron-right" class="h-4 w-4" />
        </RouterLink>
      </div>
    </section>

    <section class="flex items-center justify-center bg-slate-50 px-4 py-10 text-slate-950 dark:bg-slate-950 dark:text-white">
      <div class="w-full max-w-md">
        <div class="mb-8 flex items-center gap-3 lg:hidden">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white p-1 shadow-sm">
            <img src="/logo-mark.png" alt="FixFast" class="h-full w-full object-contain" />
          </div>
          <div>
            <p class="font-semibold">FixFast</p>
            <p class="text-sm text-slate-500">Panel del equipo del taller</p>
          </div>
        </div>

        <BaseCard content-class="p-6">
          <div class="mb-6">
            <h2 class="text-2xl font-semibold text-slate-950 dark:text-white">Iniciar sesion</h2>
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Accede al panel administrativo del taller.</p>
          </div>

          <form class="space-y-4" @submit.prevent="submit">
            <BaseInput v-model="form.email" label="Correo" type="email" placeholder="admin@fixfast.com" required />

            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-200">Contrasena</label>
              <div class="relative">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Tu contrasena"
                  autocomplete="current-password"
                  required
                  class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-3 pr-10 text-sm outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950"
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 flex w-10 items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                  :title="showPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'"
                  @click="showPassword = !showPassword"
                >
                  <AppIcon :name="showPassword ? 'eye-off' : 'eye'" class="h-4 w-4" />
                </button>
              </div>
            </div>

            <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-200">{{ error }}</p>
            <BaseButton class="w-full" type="submit" size="lg" :loading="auth.loading">Entrar al sistema</BaseButton>
          </form>
        </BaseCard>

        <p class="mt-6 text-center text-sm text-slate-500 dark:text-slate-400 lg:hidden">
          ¿Sos cliente y queres ver el estado de tu reparacion?
          <RouterLink :to="{ name: 'seguimiento' }" class="font-medium text-brand-600 hover:underline dark:text-brand-400">Consultalo aca</RouterLink>
        </p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const error = ref('')
const showPassword = ref(false)
const form = reactive({ email: '', password: '' })

async function submit() {
  error.value = ''

  try {
    await auth.login(form)
    router.push(route.query.redirect || { name: 'dashboard' })
  } catch (err) {
    error.value = err.message || 'Credenciales invalidas o API no disponible.'
  }
}
</script>
