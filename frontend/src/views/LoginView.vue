<template>
  <main class="grid min-h-screen bg-slate-950 text-white lg:grid-cols-[1.05fr_0.95fr]">
    <section class="hidden flex-col justify-between bg-slate-950 p-10 lg:flex">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-sm font-bold text-slate-950">FF</div>
        <div>
          <p class="font-semibold">FixFast</p>
          <p class="text-sm text-slate-400">ERP para talleres tecnicos</p>
        </div>
      </div>

      <div class="max-w-xl">
        <p class="mb-4 inline-flex rounded-full border border-white/10 px-3 py-1 text-sm text-teal-200">Operaciones, caja y reparaciones en un solo flujo</p>
        <h1 class="text-5xl font-semibold leading-tight">Controla cada equipo desde recepcion hasta entrega.</h1>
        <p class="mt-5 text-lg text-slate-300">Dashboard financiero, ordenes activas, pagos y saldos pendientes con una interfaz rapida para el dia a dia del taller.</p>
      </div>

      <div class="grid grid-cols-3 gap-3">
        <div v-for="item in stats" :key="item.label" class="rounded-xl border border-white/10 bg-white/[0.04] p-4">
          <p class="text-2xl font-semibold">{{ item.value }}</p>
          <p class="mt-1 text-sm text-slate-400">{{ item.label }}</p>
        </div>
      </div>
    </section>

    <section class="flex items-center justify-center bg-slate-50 px-4 py-10 text-slate-950 dark:bg-slate-950 dark:text-white">
      <div class="w-full max-w-md">
        <div class="mb-8 flex items-center gap-3 lg:hidden">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-sm font-bold text-white dark:bg-white dark:text-slate-950">FF</div>
          <div>
            <p class="font-semibold">FixFast</p>
            <p class="text-sm text-slate-500">Repair ERP</p>
          </div>
        </div>

        <BaseCard content-class="p-6">
          <div class="mb-6">
            <h2 class="text-2xl font-semibold text-slate-950 dark:text-white">Iniciar sesion</h2>
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Accede al panel administrativo del taller.</p>
          </div>

          <form class="space-y-4" @submit.prevent="submit">
            <BaseInput v-model="form.email" label="Usuario o email" placeholder="admin@fixfast.com" required />
            <BaseInput v-model="form.password" label="Contrasena" type="password" placeholder="Tu contrasena" required />
            <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-200">{{ error }}</p>
            <BaseButton class="w-full" type="submit" size="lg" :loading="auth.loading">Entrar al sistema</BaseButton>
          </form>
        </BaseCard>
      </div>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const error = ref('')
const form = reactive({ email: '', password: '' })

const stats = [
  { value: '24/7', label: 'Operacion' },
  { value: 'COP', label: 'Caja local' },
  { value: 'JWT', label: 'Sesion segura' },
]

async function submit() {
  error.value = ''

  try {
    await auth.login(form)
    router.push(route.query.redirect || { name: 'dashboard' })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Credenciales invalidas o API no disponible.'
  }
}
</script>
