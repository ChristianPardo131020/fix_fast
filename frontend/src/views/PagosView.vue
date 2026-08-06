<template>
  <div class="space-y-6">
    <PageHeader title="Pagos e ingresos" subtitle="Registro de recaudos y abonos recibidos por ordenes de reparacion.">
      <template #actions>
        <BaseButton icon="plus" @click="openCreate">Registrar ingreso</BaseButton>
      </template>
    </PageHeader>

    <div class="grid gap-4 md:grid-cols-3">
      <StatCard label="Total ingresos" :value="formatNumber(pagos.length)" icon="payments" tone="teal" />
      <StatCard label="Recaudo listado" :value="formatCurrency(totalPagos)" icon="cash" tone="slate" />
      <StatCard label="Metodos activos" :value="formatNumber(metodosActivos)" icon="dashboard" tone="sky" />
    </div>

    <BaseCard content-class="p-4">
      <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <label class="relative block md:w-96">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" />
          <input v-model="search" class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950" placeholder="Buscar por referencia, metodo u orden" />
        </label>
      </div>

      <BaseTable :columns="columns" :rows="filteredPagos" :loading="loading">
        <template #orden_id="{ row }"><span class="font-mono">ORD-{{ row.orden_id || row.orden?.id || '-' }}</span></template>
        <template #valor="{ row }">{{ formatCurrency(row.valor || row.monto || row.total) }}</template>
        <template #metodo_pago="{ row }">
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-200">{{ row.metodo_pago || row.metodo || 'Sin metodo' }}</span>
        </template>
        <template #referencia="{ row }">{{ row.referencia || row.reference || '-' }}</template>
        <template #fecha="{ row }">{{ formatDate(row.fecha || row.created_at) }}</template>
        <template #empty>
          <EmptyState icon="payments" title="No hay pagos" description="Registra pagos o abonos asociados a las ordenes." />
        </template>
        <template #actions="{ row }">
          <BaseButton variant="ghost" size="sm" icon="trash" @click="removePago(row)">Eliminar</BaseButton>
        </template>
      </BaseTable>
    </BaseCard>

    <BaseModal v-model="modalOpen" title="Registrar ingreso" subtitle="Asocia un pago recibido a una orden de reparacion.">
      <form class="grid gap-4" @submit.prevent="savePago">
        <BaseInput v-model="form.orden_id" label="Orden" type="select" required>
          <option value="">Selecciona una orden</option>
          <option v-for="orden in ordenes" :key="orden.id" :value="orden.id">#{{ orden.id }} - {{ orden.equipo || orden.modelo || 'Orden' }}</option>
        </BaseInput>
        <div class="grid gap-4 sm:grid-cols-2">
          <BaseInput v-model="form.valor" label="Valor" type="number" required />
          <BaseInput v-model="form.metodo_pago" label="Metodo de pago" type="select">
            <option value="Efectivo">Efectivo</option>
            <option value="Transferencia">Transferencia</option>
            <option value="Nequi">Nequi</option>
            <option value="Daviplata">Daviplata</option>
            <option value="Tarjeta">Tarjeta</option>
          </BaseInput>
        </div>
        <BaseInput v-model="form.referencia" label="Referencia" placeholder="Numero de comprobante o nota" />
        <BaseInput v-model="form.observaciones" label="Observaciones" textarea />
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="modalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="saving">Guardar ingreso</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseTable from '../components/BaseTable.vue'
import EmptyState from '../components/EmptyState.vue'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import { ordenesApi, pagosApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'
import { useUiStore } from '../stores/ui'

const { formatCurrency, formatDate, formatNumber } = useFormatters()
const { loading, run } = useApiState()
const ui = useUiStore()
const route = useRoute()
const router = useRouter()
const pagos = ref([])
const ordenes = ref([])
const search = ref('')
const modalOpen = ref(false)
const saving = ref(false)
const form = reactive({ orden_id: '', valor: 0, metodo_pago: 'Efectivo', referencia: '', observaciones: '' })

const columns = [
  { key: 'orden_id', label: 'Orden' },
  { key: 'valor', label: 'Valor' },
  { key: 'metodo_pago', label: 'Metodo' },
  { key: 'referencia', label: 'Referencia' },
  { key: 'fecha', label: 'Fecha' },
]

const filteredPagos = computed(() => {
  const term = search.value.toLowerCase().trim()
  if (!term) return pagos.value
  return pagos.value.filter((pago) => JSON.stringify(pago).toLowerCase().includes(term))
})

const totalPagos = computed(() => pagos.value.reduce((sum, pago) => sum + Number(pago.monto || pago.valor || pago.total || 0), 0))
const metodosActivos = computed(() => new Set(pagos.value.map((pago) => pago.metodo_pago || pago.metodo).filter(Boolean)).size)

function openCreate() {
  Object.assign(form, { orden_id: '', valor: 0, metodo_pago: 'Efectivo', referencia: '', observaciones: '' })
  modalOpen.value = true
}

async function loadData() {
  const [pagosResponse, ordenesResponse] = await Promise.all([run(() => pagosApi.list()), run(() => ordenesApi.list())])
  pagos.value = pagosResponse.data
  ordenes.value = ordenesResponse.data
}

async function savePago() {
  saving.value = true
  try {
    await run(() => pagosApi.create({ ...form, orden_id: Number(form.orden_id), valor: Number(form.valor || 0) }), 'Ingreso registrado')
    modalOpen.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function removePago(pago) {
  const confirmed = await ui.confirm({
    title: `Eliminar el pago #${pago.id}`,
    message: 'Esta accion no se puede deshacer.',
  })
  if (!confirmed) return
  await run(() => pagosApi.remove(pago.id), 'Pago eliminado')
  await loadData()
}

onMounted(async () => {
  try {
    await loadData()
  } catch {
    // noop, ya notificado por useApiState
  }
  // Acceso rapido desde el Dashboard: /pagos?crear=1 abre el modal de
  // "Registrar ingreso" directo. Se limpia el query despues para que un
  // refresh/atras no lo vuelva a abrir solo.
  if (route.query.crear === '1') {
    openCreate()
    const { crear, ...rest } = route.query
    router.replace({ query: rest })
  }
})
</script>
