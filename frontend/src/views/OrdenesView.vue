<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-xl font-semibold text-slate-950 dark:text-white">Ordenes</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400">Control tecnico, estados, valores y saldos por reparar.</p>
      </div>
      <BaseButton icon="plus" @click="openCreate">Nueva orden</BaseButton>
    </div>

    <BaseCard content-class="p-4">
      <div class="mb-4 grid gap-3 md:grid-cols-[1fr_220px]">
        <label class="relative block">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" />
          <input v-model="search" class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10 dark:border-slate-800 dark:bg-slate-950" placeholder="Buscar por cliente, equipo, falla o estado" />
        </label>
        <BaseInput v-model="statusFilter" type="select">
          <option value="">Todos los estados</option>
          <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
        </BaseInput>
      </div>

      <BaseTable :columns="columns" :rows="filteredOrdenes" :loading="loading">
        <template #cliente="{ row }">{{ clienteNombre(row) }}</template>
        <template #equipo="{ row }">
          <div>
            <p class="font-semibold text-slate-950 dark:text-white">{{ row.equipo || row.dispositivo || row.modelo || 'Equipo' }}</p>
            <p class="text-xs text-slate-500">{{ row.marca || row.modelo || row.imei || 'Sin detalle' }}</p>
          </div>
        </template>
        <template #estado="{ row }"><StatusBadge :value="row.estado" /></template>
        <template #valor="{ row }">{{ formatCurrency(row.valor || row.costo_total || row.total) }}</template>
        <template #saldo="{ row }">{{ formatCurrency(row.saldo || row.saldo_pendiente || 0) }}</template>
        <template #empty>
          <EmptyState icon="orders" title="No hay ordenes" description="Registra una orden para iniciar el seguimiento tecnico." />
        </template>
        <template #actions="{ row }">
          <div class="flex justify-end gap-1">
            <BaseButton variant="ghost" size="sm" icon="edit" @click="openEdit(row)">Editar</BaseButton>
            <BaseButton variant="ghost" size="sm" icon="trash" @click="removeOrden(row)">Eliminar</BaseButton>
          </div>
        </template>
      </BaseTable>
    </BaseCard>

    <BaseModal v-model="modalOpen" :title="editingId ? 'Editar orden' : 'Nueva orden'" subtitle="Informacion tecnica y financiera del equipo.">
      <form class="grid gap-4" @submit.prevent="saveOrden">
        <div>
          <BaseInput v-model="form.cliente_id" label="Cliente" type="select" required>
            <option value="">Selecciona un cliente</option>
            <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">{{ cliente.nombre || cliente.name || `Cliente ${cliente.id}` }}</option>
          </BaseInput>
          <button
            type="button"
            class="mt-1.5 text-sm font-medium text-teal-600 hover:text-teal-700 dark:text-teal-400"
            @click="toggleNewCliente"
          >
            {{ showNewCliente ? 'Cancelar' : '+ El cliente no existe, crearlo' }}
          </button>

          <div v-if="showNewCliente" class="mt-3 grid gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3 sm:grid-cols-2 dark:border-slate-800 dark:bg-slate-900">
            <BaseInput v-model="newCliente.nombre" label="Nombre del cliente" placeholder="Nombre completo" required />
            <BaseInput v-model="newCliente.telefono" label="Telefono" />
            <div class="sm:col-span-2 flex justify-end">
              <BaseButton type="button" size="sm" :loading="savingCliente" @click="saveNewCliente">Guardar cliente</BaseButton>
            </div>
          </div>
        </div>
        <div class="grid gap-4 sm:grid-cols-3">
          <BaseInput v-model="form.equipo" label="Equipo" placeholder="Celular, tablet..." required />
          <BaseInput v-model="form.marca" label="Marca" />
          <BaseInput v-model="form.modelo" label="Modelo" />
        </div>
        <BaseInput v-model="form.falla" label="Falla reportada" textarea required />
        <div class="grid gap-4 sm:grid-cols-3">
          <BaseInput v-model="form.estado" label="Estado" type="select">
            <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
          </BaseInput>
          <BaseInput v-model="form.valor" label="Valor total" type="number" />
          <BaseInput v-model="form.saldo" label="Saldo pendiente" type="number" />
        </div>
        <BaseInput v-model="form.observaciones" label="Observaciones internas" textarea />
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="modalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="saving">{{ editingId ? 'Actualizar' : 'Crear orden' }}</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseTable from '../components/BaseTable.vue'
import EmptyState from '../components/EmptyState.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { clientesApi, ordenesApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

const { formatCurrency } = useFormatters()
const { loading, run } = useApiState()
const ordenes = ref([])
const clientes = ref([])
const search = ref('')
const statusFilter = ref('')
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref(null)
const estados = ['Pendiente', 'En reparacion', 'Esperando repuesto', 'Listo', 'Entregado', 'Cancelado']

const showNewCliente = ref(false)
const savingCliente = ref(false)
const newCliente = reactive({ nombre: '', telefono: '' })

const form = reactive({ cliente_id: '', equipo: '', marca: '', modelo: '', falla: '', estado: 'Pendiente', valor: 0, saldo: 0, observaciones: '' })
const columns = [
  { key: 'cliente', label: 'Cliente' },
  { key: 'equipo', label: 'Equipo' },
  { key: 'estado', label: 'Estado' },
  { key: 'valor', label: 'Valor' },
  { key: 'saldo', label: 'Saldo' },
]

const filteredOrdenes = computed(() => {
  const term = search.value.toLowerCase().trim()
  return ordenes.value.filter((orden) => {
    const matchesSearch = !term || JSON.stringify(orden).toLowerCase().includes(term) || clienteNombre(orden).toLowerCase().includes(term)
    const matchesStatus = !statusFilter.value || orden.estado === statusFilter.value
    return matchesSearch && matchesStatus
  })
})

function clienteNombre(orden) {
  if (orden.cliente?.nombre) return orden.cliente.nombre
  const cliente = clientes.value.find((item) => Number(item.id) === Number(orden.cliente_id))
  return cliente?.nombre || cliente?.name || orden.cliente_nombre || `Cliente ${orden.cliente_id || '-'}`
}

function resetForm() {
  Object.assign(form, { cliente_id: '', equipo: '', marca: '', modelo: '', falla: '', estado: 'Pendiente', valor: 0, saldo: 0, observaciones: '' })
  editingId.value = null
  showNewCliente.value = false
  Object.assign(newCliente, { nombre: '', telefono: '' })
}

function toggleNewCliente() {
  showNewCliente.value = !showNewCliente.value
  Object.assign(newCliente, { nombre: '', telefono: '' })
}

async function saveNewCliente() {
  if (!newCliente.nombre.trim()) {
    return
  }

  savingCliente.value = true

  try {
    const response = await run(() => clientesApi.create({ ...newCliente }), 'Cliente creado correctamente')
    clientes.value.push(response.data)
    form.cliente_id = response.data.id
    showNewCliente.value = false
    Object.assign(newCliente, { nombre: '', telefono: '' })
  } finally {
    savingCliente.value = false
  }
}

function openCreate() {
  resetForm()
  modalOpen.value = true
}

function openEdit(orden) {
  editingId.value = orden.id
  Object.assign(form, {
    cliente_id: orden.cliente_id || orden.cliente?.id || '',
    equipo: orden.equipo || orden.dispositivo || '',
    marca: orden.marca || '',
    modelo: orden.modelo || '',
    falla: orden.falla || orden.descripcion || '',
    estado: orden.estado || 'Pendiente',
    valor: orden.valor || orden.costo_total || orden.total || 0,
    saldo: orden.saldo || orden.saldo_pendiente || 0,
    observaciones: orden.observaciones || '',
  })
  modalOpen.value = true
}

async function loadData() {
  const [ordenesResponse, clientesResponse] = await Promise.all([run(() => ordenesApi.list()), run(() => clientesApi.list())])
  ordenes.value = ordenesResponse.data
  clientes.value = clientesResponse.data
}

async function saveOrden() {
  saving.value = true
  const payload = { ...form, cliente_id: Number(form.cliente_id), valor: Number(form.valor || 0), saldo: Number(form.saldo || 0) }

  try {
    if (editingId.value) {
      await run(() => ordenesApi.update(editingId.value, payload), 'Orden actualizada')
    } else {
      await run(() => ordenesApi.create(payload), 'Orden creada')
    }
    modalOpen.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function removeOrden(orden) {
  if (!confirm(`Eliminar la orden #${orden.id}?`)) return
  await run(() => ordenesApi.remove(orden.id), 'Orden eliminada')
  await loadData()
}

onMounted(loadData)
</script>
