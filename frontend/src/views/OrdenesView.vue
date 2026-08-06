<template>
  <div class="space-y-6">
    <PageHeader title="Ordenes" subtitle="Control tecnico, estados, valores y saldos por reparar.">
      <template #actions>
        <div class="hidden sm:block">
          <BaseButton icon="plus" @click="openCreate">Nueva orden</BaseButton>
        </div>
      </template>
    </PageHeader>

    <FabButton label="Nueva orden" @click="openCreate" />

    <BaseCard content-class="p-4">
      <div class="grid gap-3 md:grid-cols-[1fr_220px]">
        <label class="relative block">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" />
          <input v-model="search" class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950" placeholder="Buscar por cliente, equipo, falla o estado" />
        </label>
        <BaseInput v-model="statusFilter" type="select">
          <option value="">Todos los estados</option>
          <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
        </BaseInput>
      </div>
    </BaseCard>

    <div v-if="initialLoading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div v-for="n in 6" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <div class="h-5 w-24 rounded-full bg-slate-200 dark:bg-slate-800" />
        <div class="mt-4 space-y-2">
          <div class="h-4 w-3/4 rounded bg-slate-200 dark:bg-slate-800" />
          <div class="h-3 w-1/2 rounded bg-slate-200 dark:bg-slate-800" />
        </div>
        <div class="mt-5 h-12 rounded-lg bg-slate-100 dark:bg-slate-800/60" />
        <div class="mt-4 grid grid-cols-2 gap-2">
          <div class="h-8 rounded-lg bg-slate-100 dark:bg-slate-800/60" />
          <div class="h-8 rounded-lg bg-slate-100 dark:bg-slate-800/60" />
        </div>
      </div>
    </div>
    <template v-else-if="filteredOrdenes.length">
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <OrderCard
          v-for="orden in pagedOrdenes"
          :key="orden.id"
          :orden="orden"
          :cliente-nombre="clienteNombre(orden)"
          :estados="estados"
          @edit="openEdit"
          @pagar="openPago"
          @detalles="openDetalles"
          @cambiar-estado="cambiarEstado"
        />
      </div>
      <Paginator :page="currentPage" :total-pages="totalPages" :total-items="filteredOrdenes.length" @update:page="currentPage = $event" />
    </template>
    <BaseCard v-else content-class="p-4">
      <EmptyState icon="orders" title="No hay ordenes" description="Registra una orden para iniciar el seguimiento tecnico." />
    </BaseCard>

    <!-- Crear / editar orden -->
    <BaseModal v-model="modalOpen" :title="editingId ? 'Editar orden' : 'Nueva orden'" subtitle="Informacion tecnica y financiera del equipo.">
      <form class="grid gap-4" @submit.prevent="saveOrden">
        <div>
          <BaseInput v-model="form.cliente_id" label="Cliente" type="select" required>
            <option value="">Selecciona un cliente</option>
            <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">{{ cliente.nombre || cliente.name || `Cliente ${cliente.id}` }}</option>
          </BaseInput>
          <button
            type="button"
            class="mt-1.5 text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
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
        <BaseInput v-model="form.problema" label="Falla reportada" textarea required />
        <div class="grid gap-4 sm:grid-cols-3">
          <BaseInput v-model="form.estado" label="Estado" type="select">
            <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
          </BaseInput>
          <BaseInput v-model="form.valor" label="Valor total" type="number" />
          <BaseInput
            v-model="saldoDisplay"
            label="Saldo pendiente"
            type="number"
            :disabled="!editingId"
            :hint="!editingId ? 'Valor total menos abono' : ''"
          />
        </div>
        <div v-if="!editingId" class="grid gap-4 sm:grid-cols-2">
          <BaseInput v-model="form.abono" label="Abono inicial" type="number" hint="Se registra tambien como pago en Pagos" />
          <BaseInput v-model="form.abono_metodo_pago" label="Metodo de pago del abono" type="select">
            <option value="Efectivo">Efectivo</option>
            <option value="Transferencia">Transferencia</option>
            <option value="Nequi">Nequi</option>
            <option value="Daviplata">Daviplata</option>
            <option value="Tarjeta">Tarjeta</option>
          </BaseInput>
        </div>
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="modalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="saving">{{ editingId ? 'Actualizar' : 'Crear orden' }}</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Registrar pago -->
    <BaseModal v-model="pagoModalOpen" title="Registrar pago" :subtitle="pagoTarget ? `Orden #${pagoTarget.id} · ${clienteNombre(pagoTarget)}` : ''">
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseModal from '../components/BaseModal.vue'
import EmptyState from '../components/EmptyState.vue'
import FabButton from '../components/FabButton.vue'
import OrderCard from '../components/OrderCard.vue'
import PageHeader from '../components/PageHeader.vue'
import Paginator from '../components/Paginator.vue'
import { ESTADOS_LABELS } from '../constants/estados'
import { clientesApi, ordenesApi, pagosApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

const route = useRoute()
const router = useRouter()
const { loading, run } = useApiState()
const initialLoading = ref(true)
const ordenes = ref([])
const clientes = ref([])
// Precargado con ?q= cuando se llega desde el buscador global del topbar
// (ver AppLayout.vue submitSearch).
const search = ref(typeof route.query.q === 'string' ? route.query.q : '')
// Por defecto se ve solo lo que falta atender; "Todos los estados" sigue
// disponible en el select para el que quiera ver el historial completo.
// Si se llega con una busqueda global (?q=), no se limita a Pendiente:
// el buscador del topbar espera encontrar cualquier orden, no solo las
// pendientes.
const statusFilter = ref(search.value ? '' : 'Pendiente')
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref(null)
const estados = ESTADOS_LABELS

const showNewCliente = ref(false)
const savingCliente = ref(false)
const newCliente = reactive({ nombre: '', telefono: '' })

const form = reactive({ cliente_id: '', equipo: '', marca: '', modelo: '', problema: '', estado: 'Pendiente', valor: 0, saldo: 0, abono: 0, abono_metodo_pago: 'Efectivo' })

// En creacion, "Saldo pendiente" no se tipea: se deriva de valor - abono
// para que nunca quede desincronizado del abono que se esta cargando al
// lado. En edicion se deja tal cual estaba (campo editable normal), ya
// que ahi el abono inicial no aplica -- los pagos posteriores se
// registran con el flujo de "Registrar pago" existente.
const saldoDisplay = computed({
  get: () => (editingId.value ? form.saldo : Math.max(Number(form.valor || 0) - Number(form.abono || 0), 0)),
  set: (value) => { form.saldo = value },
})

const pagoModalOpen = ref(false)
const savingPago = ref(false)
const pagoTarget = ref(null)
const pagoForm = reactive({ valor: 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '' })

const filteredOrdenes = computed(() => {
  const term = search.value.toLowerCase().trim()
  return ordenes.value.filter((orden) => {
    const matchesSearch = !term || JSON.stringify(orden).toLowerCase().includes(term) || clienteNombre(orden).toLowerCase().includes(term)
    const matchesStatus = !statusFilter.value || orden.estado === statusFilter.value
    return matchesSearch && matchesStatus
  })
})

const PAGE_SIZE = 12
const currentPage = ref(1)
const totalPages = computed(() => Math.max(Math.ceil(filteredOrdenes.value.length / PAGE_SIZE), 1))
const pagedOrdenes = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredOrdenes.value.slice(start, start + PAGE_SIZE)
})

// Si cambia la busqueda/filtro (o se crea/borra una orden), la pagina
// actual puede dejar de existir - se vuelve a la 1.
watch(filteredOrdenes, () => {
  currentPage.value = 1
})

function clienteNombre(orden) {
  if (orden.cliente?.nombre) return orden.cliente.nombre
  const cliente = clientes.value.find((item) => Number(item.id) === Number(orden.cliente_id))
  return cliente?.nombre || cliente?.name || orden.cliente_nombre || `Cliente ${orden.cliente_id || '-'}`
}

function resetForm() {
  Object.assign(form, { cliente_id: '', equipo: '', marca: '', modelo: '', problema: '', estado: 'Pendiente', valor: 0, saldo: 0, abono: 0, abono_metodo_pago: 'Efectivo' })
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
    equipo: orden.equipo || '',
    marca: orden.marca || '',
    modelo: orden.modelo || '',
    problema: orden.problema || '',
    estado: orden.estado || 'Pendiente',
    valor: orden.valor || 0,
    saldo: orden.saldo || 0,
    abono: 0,
    abono_metodo_pago: 'Efectivo',
  })
  modalOpen.value = true
}

function openPago(orden) {
  pagoTarget.value = orden
  Object.assign(pagoForm, { valor: orden.saldo || 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '' })
  pagoModalOpen.value = true
}

function openDetalles(orden) {
  router.push({ name: 'orden-detalle', params: { id: orden.id } })
}

async function loadData() {
  try {
    const [ordenesResponse, clientesResponse] = await Promise.all([run(() => ordenesApi.list()), run(() => clientesApi.list())])
    ordenes.value = ordenesResponse.data
    clientes.value = clientesResponse.data
  } finally {
    initialLoading.value = false
  }
}

async function saveOrden() {
  saving.value = true
  const valorNum = Number(form.valor || 0)
  const abonoNum = editingId.value ? 0 : Number(form.abono || 0)
  // El backend no conoce "abono" (no es un campo de Orden) -- solo se usa
  // aca para mostrar el saldo previsto y, despues de crear la orden,
  // para registrar el pago correspondiente.
  const { abono, abono_metodo_pago, ...ordenFields } = form
  const payload = {
    ...ordenFields,
    cliente_id: Number(form.cliente_id),
    valor: valorNum,
    // Al crear, el saldo arranca en el valor total. Si hay abono, se
    // registra aparte como Pago (mas abajo) y es crear_pago() quien
    // descuenta el saldo (misma logica que "Registrar pago" en
    // cualquier otra orden) -- restarlo tambien aca lo descontaria
    // dos veces.
    saldo: editingId.value ? Number(form.saldo || 0) : valorNum,
  }

  try {
    if (editingId.value) {
      await run(() => ordenesApi.update(editingId.value, payload), 'Orden actualizada')
    } else {
      const response = await run(() => ordenesApi.create(payload), 'Orden creada')
      if (abonoNum > 0) {
        await run(() => pagosApi.create({
          orden_id: response.data.id,
          valor: abonoNum,
          metodo_pago: form.abono_metodo_pago || 'Efectivo',
          observaciones: 'Abono inicial al crear la orden',
        }), 'Abono registrado')
      }
    }
    modalOpen.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function savePago() {
  if (!pagoTarget.value) return
  savingPago.value = true

  try {
    await run(() => pagosApi.create({ ...pagoForm, orden_id: pagoTarget.value.id, valor: Number(pagoForm.valor || 0) }), 'Pago registrado')
    pagoModalOpen.value = false
    await loadData()
  } finally {
    savingPago.value = false
  }
}

async function cambiarEstado({ orden, estado }) {
  await run(
    () => ordenesApi.update(orden.id, {
      cliente_id: orden.cliente_id,
      numero_orden: orden.numero_orden,
      equipo: orden.equipo,
      marca: orden.marca,
      modelo: orden.modelo,
      problema: orden.problema,
      diagnostico: orden.diagnostico,
      estado,
      valor: orden.valor,
      saldo: orden.saldo,
      tecnico_id: orden.tecnico_id,
    }),
    'Estado actualizado',
  )
  await loadData()
}

onMounted(async () => {
  // loadData ya reporta sus propios errores (toast, via useApiState) y
  // relanza — se atrapa aca para que una carga fallida no le tape el
  // acceso rapido de abajo al usuario.
  try {
    await loadData()
  } catch {
    // noop, ya notificado
  }
  // Acceso rapido desde el Dashboard: /ordenes?crear=1 abre el modal
  // de "Nueva orden" directo, sin que el usuario tenga que buscar el
  // boton. Se limpia el query despues para que un refresh/atras no lo
  // vuelva a abrir solo.
  if (route.query.crear === '1') {
    openCreate()
    const { crear, ...rest } = route.query
    router.replace({ query: rest })
  }
})
</script>
