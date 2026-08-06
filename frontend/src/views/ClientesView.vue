<template>
  <div class="space-y-6">
    <PageHeader title="Clientes" subtitle="Base de datos operativa para recepcion y seguimiento.">
      <template #actions>
        <div class="hidden sm:block">
          <BaseButton icon="plus" @click="openCreate">Crear cliente</BaseButton>
        </div>
      </template>
    </PageHeader>

    <FabButton label="Crear cliente" @click="openCreate" />

    <BaseCard content-class="p-4">
      <div class="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <label class="relative block md:w-80">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" />
          <input v-model="search" class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950" placeholder="Buscar por nombre, telefono o direccion" />
        </label>
        <p class="text-sm text-slate-500">{{ filteredClientes.length }} clientes</p>
      </div>

      <BaseTable :columns="columns" :rows="filteredClientes" :loading="loading">
        <template #nombre="{ row }">
          <RouterLink :to="{ name: 'cliente-detalle', params: { id: row.id } }" class="flex items-center gap-3 hover:underline">
            <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700 dark:bg-brand-500/15 dark:text-brand-300">
              {{ initials(row) }}
            </span>
            <span class="min-w-0">
              <p class="truncate font-semibold text-slate-950 dark:text-white">{{ row.nombre || row.name || 'Cliente sin nombre' }}</p>
              <p class="truncate font-mono text-xs text-slate-500">CLI-{{ row.id }}</p>
            </span>
          </RouterLink>
        </template>
        <template #telefono="{ row }">{{ row.telefono || row.phone || '-' }}</template>
        <template #direccion="{ row }">{{ row.direccion || row.address || '-' }}</template>
        <template #empty>
          <EmptyState icon="users" title="No hay clientes" description="Crea el primer cliente para empezar a registrar ordenes." />
        </template>
        <template #actions="{ row }">
          <div class="flex justify-end gap-2">
            <BaseButton variant="ghost" size="sm" icon="edit" @click="openEdit(row)">Editar</BaseButton>
            <BaseButton variant="ghost" size="sm" icon="trash" @click="removeCliente(row)">Eliminar</BaseButton>
          </div>
        </template>
      </BaseTable>
    </BaseCard>

    <BaseModal v-model="modalOpen" :title="editingId ? 'Editar cliente' : 'Crear cliente'" subtitle="Datos basicos para contacto y facturacion.">
      <form class="grid gap-4" @submit.prevent="saveCliente">
        <BaseInput v-model="form.nombre" label="Nombre completo" required />
        <BaseInput v-model="form.telefono" label="Telefono" />
        <BaseInput v-model="form.direccion" label="Direccion" />
        <BaseInput v-model="form.observaciones" label="Notas" textarea />
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="modalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="saving">{{ editingId ? 'Guardar cambios' : 'Guardar cliente' }}</BaseButton>
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
import FabButton from '../components/FabButton.vue'
import PageHeader from '../components/PageHeader.vue'
import { clientesApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useUiStore } from '../stores/ui'

const route = useRoute()
const router = useRouter()
const clientes = ref([])
const search = ref('')
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref(null)
const { loading, run } = useApiState()
const ui = useUiStore()

// "observaciones" es el nombre real del campo en el backend (ver
// Cliente en app/models/cliente.py). El campo "email" se saco del
// formulario porque el modelo de Cliente no tiene esa columna: se
// tipeaba pero el backend lo descartaba en silencio, nunca quedaba
// guardado.
const form = reactive({ nombre: '', telefono: '', direccion: '', observaciones: '' })
const columns = [
  { key: 'nombre', label: 'Cliente' },
  { key: 'telefono', label: 'Telefono' },
  { key: 'direccion', label: 'Direccion' },
]

const filteredClientes = computed(() => {
  const term = search.value.toLowerCase().trim()
  if (!term) return clientes.value
  return clientes.value.filter((cliente) => (
    cliente.nombre?.toLowerCase().includes(term)
    || cliente.telefono?.toLowerCase().includes(term)
    || cliente.direccion?.toLowerCase().includes(term)
  ))
})

function initials(cliente) {
  const name = cliente?.nombre || cliente?.name || '?'
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
}

function resetForm() {
  Object.assign(form, { nombre: '', telefono: '', direccion: '', observaciones: '' })
}

function openCreate() {
  editingId.value = null
  resetForm()
  modalOpen.value = true
}

function openEdit(cliente) {
  editingId.value = cliente.id
  Object.assign(form, {
    nombre: cliente.nombre || '',
    telefono: cliente.telefono || '',
    direccion: cliente.direccion || '',
    observaciones: cliente.observaciones || '',
  })
  modalOpen.value = true
}

async function loadClientes() {
  const response = await run(() => clientesApi.list())
  clientes.value = response.data
}

async function saveCliente() {
  saving.value = true
  try {
    if (editingId.value) {
      await run(() => clientesApi.update(editingId.value, { ...form }), 'Cliente actualizado')
    } else {
      await run(() => clientesApi.create({ ...form }), 'Cliente creado correctamente')
    }
    modalOpen.value = false
    await loadClientes()
  } finally {
    saving.value = false
  }
}

async function removeCliente(cliente) {
  const nombre = cliente.nombre || cliente.name || 'este cliente'
  const confirmed = await ui.confirm({
    title: `Eliminar a ${nombre}`,
    message: 'Esta accion no se puede deshacer. El cliente se eliminara de forma permanente.',
  })
  if (!confirmed) return
  await run(() => clientesApi.remove(cliente.id), 'Cliente eliminado')
  await loadClientes()
}

onMounted(async () => {
  try {
    await loadClientes()
  } catch {
    // noop, ya notificado por useApiState
  }
  // Atajo desde la ficha de un cliente (ClienteDetalleView "Editar"):
  // /clientes?editar=<id> abre el modal de edicion ya cargado con ese
  // cliente. Se limpia el query despues para que un refresh/atras no lo
  // vuelva a abrir solo.
  const editarId = route.query.editar
  if (editarId) {
    const cliente = clientes.value.find((c) => String(c.id) === String(editarId))
    if (cliente) openEdit(cliente)
    const { editar, ...rest } = route.query
    router.replace({ query: rest })
  }
})
</script>
