<template>
  <div class="space-y-6">
    <BaseCard v-if="notFound" content-class="p-6">
      <EmptyState icon="users" title="Cliente no encontrado" description="Puede que el cliente haya sido eliminado." />
      <div class="mt-4 flex justify-center">
        <BaseButton variant="secondary" @click="router.push({ name: 'clientes' })">Volver a clientes</BaseButton>
      </div>
    </BaseCard>

    <template v-else>
      <div class="flex items-center gap-4">
        <button type="button" class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900" title="Volver" @click="router.push({ name: 'clientes' })">
          <AppIcon name="chevron-left" />
        </button>
        <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-brand-100 text-lg font-semibold text-brand-700 dark:bg-brand-500/15 dark:text-brand-300">
          {{ initials }}
        </div>
        <div class="min-w-0">
          <h2 class="truncate text-xl font-semibold text-slate-950 dark:text-white">{{ cliente?.nombre || 'Cliente' }}</h2>
          <p class="truncate text-sm text-slate-500 dark:text-slate-400">{{ cliente?.telefono || 'Sin telefono' }} · {{ cliente?.direccion || 'Sin direccion' }}</p>
        </div>
      </div>

      <section class="grid gap-4 sm:grid-cols-3">
        <StatCard label="Equipos totales" :value="formatNumber(ordenesCliente.length)" icon="orders" tone="brand" />
        <StatCard label="Equipos activos" :value="formatNumber(equiposActivos.length)" icon="wrench" tone="orange" />
        <StatCard label="Dinero gastado" :value="formatCurrency(dineroGastado)" icon="cash" tone="green" />
      </section>

      <section class="grid gap-6 lg:grid-cols-2">
        <BaseCard title="Equipos activos" subtitle="Ordenes en curso de este cliente">
          <div v-if="equiposActivos.length" class="divide-y divide-slate-100 dark:divide-slate-800">
            <div v-for="orden in equiposActivos" :key="orden.id" class="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">{{ orden.equipo || 'Equipo' }}</p>
                <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ formatCurrency(orden.saldo) }} pendiente</p>
              </div>
              <StatusBadge :value="orden.estado" />
            </div>
          </div>
          <EmptyState v-else icon="wrench" title="Sin equipos activos" description="Este cliente no tiene ordenes en curso." />
        </BaseCard>

        <BaseCard title="Historial de pagos" subtitle="Pagos registrados de este cliente">
          <div v-if="pagosCliente.length" class="divide-y divide-slate-100 dark:divide-slate-800">
            <div v-for="pago in pagosCliente" :key="pago.id" class="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">{{ formatCurrency(pago.valor) }}</p>
                <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ pago.metodo_pago || 'Sin metodo' }}{{ pago.referencia_pago ? ` · ${pago.referencia_pago}` : '' }}</p>
              </div>
              <span class="shrink-0 text-xs text-slate-400">{{ formatDate(pago.created_at) }}</span>
            </div>
          </div>
          <EmptyState v-else icon="payments" title="Sin pagos" description="Todavia no se registraron pagos de este cliente." />
        </BaseCard>
      </section>

      <BaseCard title="Ultimas reparaciones" subtitle="Historial completo de ordenes">
        <div v-if="ordenesRecientes.length" class="divide-y divide-slate-100 dark:divide-slate-800">
          <div v-for="orden in ordenesRecientes" :key="orden.id" class="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">#{{ orden.id }} · {{ orden.equipo || 'Equipo' }}</p>
              <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ formatDate(orden.fecha_ingreso) }}</p>
            </div>
            <div class="flex shrink-0 items-center gap-3">
              <span class="text-sm font-semibold text-slate-950 dark:text-white">{{ formatCurrency(orden.valor) }}</span>
              <StatusBadge :value="orden.estado" />
            </div>
          </div>
        </div>
        <EmptyState v-else icon="orders" title="Sin reparaciones" description="Este cliente todavia no tiene ordenes registradas." />
      </BaseCard>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import EmptyState from '../components/EmptyState.vue'
import StatCard from '../components/StatCard.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { clientesApi, ordenesApi, pagosApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const router = useRouter()
const { formatCurrency, formatDate, formatNumber } = useFormatters()
const { run } = useApiState()

const cliente = ref(null)
const ordenes = ref([])
const pagos = ref([])
const notFound = ref(false)

const initials = computed(() => {
  const name = cliente.value?.nombre || '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
})

const ordenesCliente = computed(() => ordenes.value.filter((orden) => Number(orden.cliente_id) === Number(props.id)))

const equiposActivos = computed(() =>
  ordenesCliente.value.filter((orden) => !['entreg', 'cancel'].some((s) => (orden.estado || '').toLowerCase().includes(s))),
)

const ordenesRecientes = computed(() =>
  [...ordenesCliente.value].sort((a, b) => new Date(b.fecha_ingreso || 0) - new Date(a.fecha_ingreso || 0)).slice(0, 8),
)

// Los pagos no tienen cliente_id directo (se asocian via orden_id), asi
// que se cruzan con las ordenes de este cliente. Es el mismo dataset
// que usa "dinero gastado" arriba, para que el numero y la lista
// siempre coincidan.
const pagosCliente = computed(() => {
  const ordenIds = new Set(ordenesCliente.value.map((orden) => orden.id))
  return pagos.value
    .filter((pago) => ordenIds.has(pago.orden_id))
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
})

const dineroGastado = computed(() => pagosCliente.value.reduce((sum, pago) => sum + Number(pago.valor || 0), 0))

onMounted(async () => {
  try {
    const [clienteResponse, ordenesResponse, pagosResponse] = await Promise.all([
      run(() => clientesApi.get(props.id)),
      run(() => ordenesApi.list()),
      run(() => pagosApi.list()),
    ])
    cliente.value = clienteResponse.data
    ordenes.value = ordenesResponse.data
    pagos.value = pagosResponse.data
  } catch {
    notFound.value = true
  }
})
</script>
