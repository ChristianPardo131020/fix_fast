<template>
  <div class="space-y-6">
    <BaseCard v-if="notFound" content-class="p-6">
      <EmptyState icon="orders" title="Orden no encontrada" description="Puede que la orden haya sido eliminada." />
      <div class="mt-4 flex justify-center">
        <BaseButton variant="secondary" @click="router.push({ name: 'ordenes' })">Volver a ordenes</BaseButton>
      </div>
    </BaseCard>

    <template v-else-if="orden">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div class="flex items-start gap-4">
          <button type="button" class="mt-1 rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900" title="Volver" @click="router.push({ name: 'ordenes' })">
            <AppIcon name="chevron-left" />
          </button>
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300">
            <AppIcon name="wrench" />
          </div>
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="truncate text-xl font-semibold text-slate-950 dark:text-white">Orden #{{ orden.id }} · {{ orden.equipo || 'Equipo' }}</h2>
              <StatusBadge :value="orden.estado" />
            </div>
            <p class="truncate text-sm text-slate-500 dark:text-slate-400">
              <RouterLink v-if="orden.cliente_id" :to="{ name: 'cliente-detalle', params: { id: orden.cliente_id } }" class="hover:underline">{{ clienteNombre }}</RouterLink>
              <span v-else>{{ clienteNombre }}</span>
              · {{ orden.marca || 'Sin marca' }}{{ orden.modelo ? ` ${orden.modelo}` : '' }}
            </p>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <BaseButton variant="secondary" size="sm" icon="edit" @click="openEdit">Editar</BaseButton>
          <BaseButton variant="secondary" size="sm" icon="payments" @click="openPago">Registrar pago</BaseButton>
          <BaseButton variant="ghost" size="sm" icon="refresh" @click="abrirCambioEstado">Cambiar estado</BaseButton>
        </div>
      </div>

      <div v-if="cambiandoEstado" class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-950">
        <BaseInput v-model="nuevoEstado" type="select" class="flex-1">
          <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
        </BaseInput>
        <BaseButton size="sm" :loading="cambiandoEstadoGuardando" @click="confirmarEstado">Guardar</BaseButton>
        <BaseButton variant="ghost" size="sm" @click="cambiandoEstado = false">Cancelar</BaseButton>
      </div>

      <section class="grid gap-4 sm:grid-cols-3">
        <StatCard label="Valor total" :value="formatCurrency(orden.valor)" icon="cash" tone="brand" />
        <StatCard label="Saldo pendiente" :value="formatCurrency(orden.saldo)" icon="wallet" :tone="Number(orden.saldo) > 0 ? 'orange' : 'green'" />
        <StatCard label="Dias en taller" :value="`${diasEnTaller} dias`" icon="clock" tone="purple" />
      </section>

      <div class="inline-flex gap-1 rounded-xl bg-slate-100 p-1 dark:bg-slate-900">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          type="button"
          class="rounded-lg px-3.5 py-1.5 text-sm font-medium transition"
          :class="activeTab === tab.key ? 'bg-white text-slate-950 shadow-soft dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Resumen -->
      <section v-if="activeTab === 'resumen'" class="grid gap-6 lg:grid-cols-2">
        <BaseCard title="Falla reportada" subtitle="Descripcion entregada por el cliente">
          <p class="rounded-lg bg-slate-50 p-3 text-sm text-slate-700 dark:bg-slate-900 dark:text-slate-200">{{ orden.problema || 'Sin descripcion' }}</p>
        </BaseCard>
        <BaseCard title="Diagnostico tecnico" subtitle="Notas del taller sobre el equipo">
          <p class="rounded-lg bg-slate-50 p-3 text-sm text-slate-700 dark:bg-slate-900 dark:text-slate-200">{{ orden.diagnostico || 'Sin diagnostico aun' }}</p>
        </BaseCard>
      </section>

      <!-- Pagos -->
      <section v-if="activeTab === 'pagos'">
        <BaseCard title="Historial de pagos" subtitle="Todos los pagos registrados para esta orden">
          <div v-if="pagosOrden.length" class="divide-y divide-slate-100 dark:divide-slate-800">
            <div v-for="pago in pagosOrden" :key="pago.id" class="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">{{ formatCurrency(pago.valor) }}</p>
                <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ pago.metodo_pago || 'Sin metodo' }}{{ pago.referencia_pago ? ` · ${pago.referencia_pago}` : '' }}{{ pago.observaciones ? ` · ${pago.observaciones}` : '' }}</p>
              </div>
              <span class="shrink-0 text-xs text-slate-400">{{ formatDate(pago.created_at) }}</span>
            </div>
          </div>
          <EmptyState v-else icon="payments" title="Sin pagos" description="Todavia no se registraron pagos para esta orden." />
        </BaseCard>
      </section>

      <!-- Timeline -->
      <section v-if="activeTab === 'timeline'">
        <BaseCard title="Linea de tiempo" subtitle="Eventos reales de esta orden, en orden cronologico">
          <div v-if="timelineEvents.length" class="space-y-0">
            <div v-for="(event, index) in timelineEvents" :key="event.id" class="flex gap-3">
              <div class="flex flex-col items-center">
                <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300">
                  <AppIcon :name="event.icon" class="h-4 w-4" />
                </span>
                <span v-if="index < timelineEvents.length - 1" class="w-px flex-1 bg-slate-200 dark:bg-slate-800" />
              </div>
              <div class="pb-6">
                <p class="text-sm font-semibold text-slate-950 dark:text-white">{{ event.label }}</p>
                <p class="text-sm text-slate-500 dark:text-slate-400">{{ event.detail }}</p>
                <p class="mt-0.5 text-xs text-slate-400">{{ formatDate(event.date) }}</p>
              </div>
            </div>
          </div>
          <EmptyState v-else icon="clock" title="Sin eventos" description="Todavia no hay eventos registrados para esta orden." />
        </BaseCard>
      </section>
    </template>

    <!-- Editar orden -->
    <BaseModal v-model="editModalOpen" title="Editar orden" subtitle="Informacion tecnica y financiera del equipo.">
      <form class="grid gap-4" @submit.prevent="saveEdit">
        <BaseInput v-model="editForm.cliente_id" label="Cliente" type="select" required>
          <option value="">Selecciona un cliente</option>
          <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">{{ cliente.nombre || cliente.name || `Cliente ${cliente.id}` }}</option>
        </BaseInput>
        <div class="grid gap-4 sm:grid-cols-3">
          <BaseInput v-model="editForm.equipo" label="Equipo" required />
          <BaseInput v-model="editForm.marca" label="Marca" />
          <BaseInput v-model="editForm.modelo" label="Modelo" />
        </div>
        <BaseInput v-model="editForm.problema" label="Falla reportada" textarea required />
        <BaseInput v-model="editForm.diagnostico" label="Diagnostico tecnico" textarea />
        <div class="grid gap-4 sm:grid-cols-3">
          <BaseInput v-model="editForm.estado" label="Estado" type="select">
            <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
          </BaseInput>
          <BaseInput v-model="editForm.valor" label="Valor total" type="number" />
          <BaseInput v-model="editForm.saldo" label="Saldo pendiente" type="number" />
        </div>
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="editModalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="savingEdit">Guardar cambios</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Registrar pago -->
    <BaseModal v-model="pagoModalOpen" title="Registrar pago" :subtitle="orden ? `Orden #${orden.id} · ${clienteNombre}` : ''">
      <form class="grid gap-4" @submit.prevent="savePago">
        <div class="grid gap-4 sm:grid-cols-2">
          <BaseInput v-model="pagoForm.valor" label="Valor" type="number" required />
          <BaseInput v-model="pagoForm.metodo_pago" label="Metodo de pago" type="select">
            <option value="Efectivo">Efectivo</option>
            <option value="Transferencia">Transferencia</option>
            <option value="Nequi">Nequi</option>
            <option value="Daviplata">Daviplata</option>
            <option value="Tarjeta">Tarjeta</option>
          </BaseInput>
        </div>
        <BaseInput v-model="pagoForm.referencia_pago" label="Referencia" placeholder="Numero de comprobante o nota" />
        <BaseInput v-model="pagoForm.observaciones" label="Observaciones" textarea />
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="pagoModalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="savingPago">Guardar pago</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseModal from '../components/BaseModal.vue'
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
const { formatCurrency, formatDate } = useFormatters()
const { run } = useApiState()

const estados = ['Pendiente', 'En reparacion', 'Esperando repuesto', 'Listo', 'Entregado', 'Cancelado']
const tabs = [
  { key: 'resumen', label: 'Resumen' },
  { key: 'pagos', label: 'Pagos' },
  { key: 'timeline', label: 'Linea de tiempo' },
]

const orden = ref(null)
const clientes = ref([])
const pagos = ref([])
const notFound = ref(false)
const activeTab = ref('resumen')

const cambiandoEstado = ref(false)
const cambiandoEstadoGuardando = ref(false)
const nuevoEstado = ref('')

const editModalOpen = ref(false)
const savingEdit = ref(false)
const editForm = reactive({ cliente_id: '', equipo: '', marca: '', modelo: '', problema: '', diagnostico: '', estado: 'Pendiente', valor: 0, saldo: 0 })

const pagoModalOpen = ref(false)
const savingPago = ref(false)
const pagoForm = reactive({ valor: 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '' })

const clienteNombre = computed(() => {
  if (!orden.value) return 'Cliente'
  const cliente = clientes.value.find((item) => Number(item.id) === Number(orden.value.cliente_id))
  return cliente?.nombre || cliente?.name || `Cliente ${orden.value.cliente_id || '-'}`
})

// Igual que en OrderCard.vue: con fecha de entrega, es la duracion real
// de la reparacion; sin ella (orden activa), sigue contando hasta hoy.
const diasEnTaller = computed(() => {
  if (!orden.value?.fecha_ingreso) return 0
  const fin = orden.value.fecha_entrega ? new Date(orden.value.fecha_entrega).getTime() : Date.now()
  const ms = fin - new Date(orden.value.fecha_ingreso).getTime()
  return Math.max(Math.floor(ms / 86_400_000), 0)
})

const pagosOrden = computed(() => {
  if (!orden.value) return []
  return pagos.value
    .filter((pago) => Number(pago.orden_id) === Number(orden.value.id))
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
})

// No hay endpoint de historial de estados en el backend (la tabla
// existe pero nada la llena todavia), asi que la linea de tiempo se
// arma solo con eventos reales que si tenemos: ingreso, pagos y
// entrega. Nada inventado.
const timelineEvents = computed(() => {
  if (!orden.value) return []
  const events = [
    { id: 'creada', label: 'Orden creada', detail: `${orden.value.equipo || 'Equipo'} ingreso al taller`, date: orden.value.fecha_ingreso, icon: 'orders' },
  ]

  pagosOrden.value.forEach((pago) => {
    events.push({
      id: `pago-${pago.id}`,
      label: 'Pago registrado',
      detail: `${formatCurrency(pago.valor)} · ${pago.metodo_pago || 'Sin metodo'}`,
      date: pago.created_at,
      icon: 'payments',
    })
  })

  if (orden.value.fecha_entrega) {
    events.push({ id: 'entrega', label: 'Equipo entregado', detail: 'Orden finalizada', date: orden.value.fecha_entrega, icon: 'check' })
  }

  return events.sort((a, b) => new Date(a.date || 0) - new Date(b.date || 0))
})

function abrirCambioEstado() {
  nuevoEstado.value = orden.value?.estado || estados[0]
  cambiandoEstado.value = true
}

async function confirmarEstado() {
  cambiandoEstadoGuardando.value = true
  try {
    await run(() => ordenesApi.update(orden.value.id, { ...ordenPayload(orden.value), estado: nuevoEstado.value }), 'Estado actualizado')
    cambiandoEstado.value = false
    await loadOrden()
  } finally {
    cambiandoEstadoGuardando.value = false
  }
}

function ordenPayload(source) {
  return {
    cliente_id: source.cliente_id,
    numero_orden: source.numero_orden,
    equipo: source.equipo,
    marca: source.marca,
    modelo: source.modelo,
    problema: source.problema,
    diagnostico: source.diagnostico,
    estado: source.estado,
    valor: source.valor,
    saldo: source.saldo,
    tecnico_id: source.tecnico_id,
  }
}

function openEdit() {
  Object.assign(editForm, {
    cliente_id: orden.value.cliente_id || '',
    equipo: orden.value.equipo || '',
    marca: orden.value.marca || '',
    modelo: orden.value.modelo || '',
    problema: orden.value.problema || '',
    diagnostico: orden.value.diagnostico || '',
    estado: orden.value.estado || 'Pendiente',
    valor: orden.value.valor || 0,
    saldo: orden.value.saldo || 0,
  })
  editModalOpen.value = true
}

async function saveEdit() {
  savingEdit.value = true
  const payload = { ...editForm, cliente_id: Number(editForm.cliente_id), valor: Number(editForm.valor || 0), saldo: Number(editForm.saldo || 0) }
  try {
    await run(() => ordenesApi.update(orden.value.id, payload), 'Orden actualizada')
    editModalOpen.value = false
    await loadOrden()
  } finally {
    savingEdit.value = false
  }
}

function openPago() {
  Object.assign(pagoForm, { valor: orden.value.saldo || 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '' })
  pagoModalOpen.value = true
}

async function savePago() {
  savingPago.value = true
  try {
    await run(() => pagosApi.create({ ...pagoForm, orden_id: orden.value.id, valor: Number(pagoForm.valor || 0) }), 'Pago registrado')
    pagoModalOpen.value = false
    await Promise.all([loadOrden(), loadPagos()])
  } finally {
    savingPago.value = false
  }
}

async function loadOrden() {
  const response = await ordenesApi.get(props.id)
  orden.value = response.data
}

async function loadPagos() {
  const response = await pagosApi.list()
  pagos.value = response.data
}

onMounted(async () => {
  try {
    const [, clientesResponse] = await Promise.all([loadOrden(), run(() => clientesApi.list()), loadPagos()])
    clientes.value = clientesResponse.data
  } catch {
    notFound.value = true
  }
})
</script>
