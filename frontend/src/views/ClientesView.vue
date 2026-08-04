<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 class="text-xl font-semibold text-slate-950 dark:text-white">Clientes</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400">Base de datos operativa para recepcion y seguimiento.</p>
      </div>
      <BaseButton icon="plus" @click="openCreate">Crear cliente</BaseButton>
    </div>

    <BaseCard content-class="p-4">
      <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <label class="relative block md:w-80">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" />
          <input v-model="search" class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-500/10 dark:border-slate-800 dark:bg-slate-950" placeholder="Buscar por nombre, telefono o email" />
        </label>
        <p class="text-sm text-slate-500">{{ filteredClientes.length }} clientes</p>
      </div>

      <BaseTable :columns="columns" :rows="filteredClientes" :loading="loading">
        <template #nombre="{ row }">
          <div>
            <p class="font-semibold text-slate-950 dark:text-white">{{ row.nombre || row.name || 'Cliente sin nombre' }}</p>
            <p class="text-xs text-slate-500">ID {{ row.id }}</p>
          </div>
        </template>
        <template #telefono="{ row }">{{ row.telefono || row.phone || '-' }}</template>
        <template #email="{ row }">{{ row.email || row.correo || '-' }}</template>
        <template #direccion="{ row }">{{ row.direccion || row.address || '-' }}</template>
        <template #empty>
          <EmptyState icon="users" title="No hay clientes" description="Crea el primer cliente para empezar a registrar ordenes." />
        </template>
        <template #actions="{ row }">
          <BaseButton variant="ghost" size="sm" icon="trash" @click="removeCliente(row)">Eliminar</BaseButton>
        </template>
      </BaseTable>
    </BaseCard>

    <BaseModal v-model="modalOpen" title="Crear cliente" subtitle="Datos basicos para contacto y facturacion.">
      <form class="grid gap-4" @submit.prevent="saveCliente">
        <BaseInput v-model="form.nombre" label="Nombre completo" required />
        <div class="grid gap-4 sm:grid-cols-2">
          <BaseInput v-model="form.telefono" label="Telefono" />
          <BaseInput v-model="form.email" label="Email" type="email" />
        </div>
        <BaseInput v-model="form.direccion" label="Direccion" />
        <BaseInput v-model="form.notas" label="Notas" textarea />
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="modalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="saving">Guardar cliente</BaseButton>
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
import { clientesApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'

const clientes = ref([])
const search = ref('')
const modalOpen = ref(false)
const saving = ref(false)
const { loading, run } = useApiState()

const form = reactive({ nombre: '', telefono: '', email: '', direccion: '', notas: '' })
const columns = [
  { key: 'nombre', label: 'Cliente' },
  { key: 'telefono', label: 'Telefono' },
  { key: 'email', label: 'Email' },
  { key: 'direccion', label: 'Direccion' },
]

const filteredClientes = computed(() => {
  const term = search.value.toLowerCase().trim()
  if (!term) return clientes.value
  return clientes.value.filter((cliente) => JSON.stringify(cliente).toLowerCase().includes(term))
})

function resetForm() {
  Object.assign(form, { nombre: '', telefono: '', email: '', direccion: '', notas: '' })
}

function openCreate() {
  resetForm()
  modalOpen.value = true
}

async function loadClientes() {
  const response = await run(() => clientesApi.list())
  clientes.value = response.data
}

async function saveCliente() {
  saving.value = true
  try {
    await run(() => clientesApi.create({ ...form }), 'Cliente creado correctamente')
    modalOpen.value = false
    await loadClientes()
  } finally {
    saving.value = false
  }
}

async function removeCliente(cliente) {
  if (!confirm(`Eliminar a ${cliente.nombre || cliente.name || 'este cliente'}?`)) return
  await run(() => clientesApi.remove(cliente.id), 'Cliente eliminado')
  await loadClientes()
}

onMounted(loadClientes)
</script>
