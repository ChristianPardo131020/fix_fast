<template>
  <main class="grid min-h-screen bg-slate-950 text-white lg:grid-cols-[1.05fr_0.95fr]">
    <section class="hidden flex-col justify-between bg-slate-950 p-10 lg:flex">
      <RouterLink :to="{ name: 'login' }" class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">FF</div>
        <div>
          <p class="font-semibold">FixFast</p>
          <p class="text-sm text-slate-400">Taller tecnico</p>
        </div>
      </RouterLink>

      <div class="max-w-xl">
        <p class="mb-4 inline-flex rounded-full border border-white/10 px-3 py-1 text-sm text-brand-200">Seguimiento de tu reparacion</p>
        <h1 class="text-5xl font-semibold leading-tight">Consulta el estado de tu equipo sin crear una cuenta.</h1>
        <p class="mt-5 text-lg text-slate-300">Con el numero de orden que te dimos al recibir tu equipo y tu telefono, podes ver en que va la reparacion en cualquier momento.</p>
      </div>

      <p class="text-sm text-slate-500">¿Sos parte del equipo del taller? <RouterLink :to="{ name: 'login' }" class="font-medium text-brand-300 hover:underline">Inicia sesion aca</RouterLink>.</p>
    </section>

    <section class="flex items-center justify-center bg-slate-50 px-4 py-10 text-slate-950 dark:bg-slate-950 dark:text-white">
      <div class="w-full max-w-md">
        <div class="mb-8 flex items-center justify-between lg:hidden">
          <RouterLink :to="{ name: 'login' }" class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-sm font-bold text-white dark:bg-white dark:text-slate-950">FF</div>
            <div>
              <p class="font-semibold">FixFast</p>
              <p class="text-sm text-slate-500">Taller tecnico</p>
            </div>
          </RouterLink>
        </div>

        <!-- Formulario de consulta -->
        <BaseCard v-if="!resultado" content-class="p-6">
          <div class="mb-6">
            <h2 class="text-2xl font-semibold text-slate-950 dark:text-white">Estado de tu reparacion</h2>
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Ingresa el numero de orden y el telefono que dejaste al recibir tu equipo.</p>
          </div>

          <form class="space-y-4" @submit.prevent="buscar">
            <BaseInput v-model="form.codigo" label="Numero de orden" placeholder="Ej. FF-000123" required />
            <BaseInput v-model="form.telefono" label="Telefono" type="tel" placeholder="Ej. 3001234567" required />
            <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-200">{{ error }}</p>
            <BaseButton class="w-full" type="submit" size="lg" :loading="loading">Consultar estado</BaseButton>
          </form>

          <p class="mt-6 text-center text-sm text-slate-500 dark:text-slate-400 lg:hidden">
            ¿Sos parte del equipo del taller? <RouterLink :to="{ name: 'login' }" class="font-medium text-brand-600 hover:underline dark:text-brand-400">Inicia sesion</RouterLink>
          </p>
        </BaseCard>

        <!-- Resultado -->
        <BaseCard v-else content-class="p-6">
          <button type="button" class="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white" @click="resultado = null">
            <AppIcon name="chevron-left" class="h-4 w-4" />
            Consultar otra orden
          </button>

          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="font-mono text-xs font-medium uppercase tracking-wide text-slate-400">Orden {{ resultado.numero_orden }}</p>
              <h2 class="mt-1 text-xl font-semibold text-slate-950 dark:text-white">{{ resultado.equipo || 'Equipo' }}</h2>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ resultado.marca || 'Sin marca' }}{{ resultado.modelo ? ` · ${resultado.modelo}` : '' }}</p>
            </div>
            <StatusBadge :value="resultado.estado" />
          </div>

          <div class="mt-5 rounded-xl border border-brand-100 bg-brand-50 p-4 text-sm text-brand-800 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-200">
            {{ mensajeAmigable }}
          </div>

          <dl class="mt-5 grid grid-cols-2 gap-4 border-t border-slate-100 pt-5 text-sm dark:border-slate-800">
            <div>
              <dt class="text-xs text-slate-400">Ingreso</dt>
              <dd class="mt-0.5 font-medium text-slate-700 dark:text-slate-200">{{ formatDate(resultado.fecha_ingreso) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-400">Entrega</dt>
              <dd class="mt-0.5 font-medium text-slate-700 dark:text-slate-200">{{ resultado.fecha_entrega ? formatDate(resultado.fecha_entrega) : 'Aun no entregado' }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-400">Valor total</dt>
              <dd class="mt-0.5 font-medium text-slate-700 dark:text-slate-200">{{ formatCurrency(resultado.valor) }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-400">Saldo pendiente</dt>
              <dd class="mt-0.5 font-semibold text-slate-950 dark:text-white">{{ formatCurrency(resultado.saldo) }}</dd>
            </div>
          </dl>
        </BaseCard>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { publicApi } from '../api/resources'
import { useFormatters } from '../composables/useFormatters'

const { formatCurrency, formatDate } = useFormatters()

const form = reactive({ codigo: '', telefono: '' })
const loading = ref(false)
const error = ref('')
const resultado = ref(null)

// Mensaje humano por estado, para que la pantalla no se sienta como un
// panel de administracion sino como algo pensado para el cliente final.
const mensajesPorEstado = [
  { match: ['cancel'], text: 'Esta orden fue cancelada. Si tenes dudas, comunicate con el taller.' },
  { match: ['entreg'], text: 'Este equipo ya fue entregado. ¡Gracias por confiar en nosotros!' },
  { match: ['listo'], text: 'Tu equipo esta listo. Ya podes pasar a recogerlo.' },
  { match: ['repuesto'], text: 'Estamos esperando un repuesto para continuar con la reparacion.' },
  { match: ['repar', 'proceso'], text: 'Tu equipo esta en reparacion en este momento.' },
]

const mensajeAmigable = computed(() => {
  const estado = (resultado.value?.estado || '').toLowerCase()
  const match = mensajesPorEstado.find((item) => item.match.some((keyword) => estado.includes(keyword)))
  return match?.text || 'Recibimos tu equipo y esta en cola de revision.'
})

async function buscar() {
  error.value = ''
  loading.value = true

  try {
    const response = await publicApi.trackOrder(form.codigo.trim(), form.telefono.trim())
    resultado.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'No pudimos consultar el estado. Intenta de nuevo en unos minutos.'
  } finally {
    loading.value = false
  }
}
</script>
