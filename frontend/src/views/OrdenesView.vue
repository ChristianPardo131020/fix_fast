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

    <FilterBar>
      <SearchField v-model="search" class="min-w-[13rem] flex-1" placeholder="Buscar por cliente, equipo, falla o estado" />
      <BaseSelect v-model="statusFilter" variant="card" class="sm:w-40">
        <option value="">Todos los estados</option>
        <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
      </BaseSelect>
      <DateRangePicker v-model="dateRange" />
    </FilterBar>

    <div v-if="initialLoading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <div v-for="n in 6" :key="n" class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <div class="skeleton h-5 w-24 rounded-full" />
        <div class="mt-4 space-y-2">
          <div class="skeleton h-4 w-3/4 rounded" />
          <div class="skeleton h-3 w-1/2 rounded" />
        </div>
        <div class="skeleton mt-5 h-12 rounded-lg" />
        <div class="mt-4 grid grid-cols-2 gap-2">
          <div class="skeleton h-8 rounded-lg" />
          <div class="skeleton h-8 rounded-lg" />
        </div>
      </div>
    </div>
    <template v-else-if="filteredOrdenes.length">
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <OrderCard
          v-for="(orden, index) in pagedOrdenes"
          :key="orden.id"
          :orden="orden"
          :index="index"
          :cliente-nombre="clienteNombre(orden)"
          :estados="estados"
          @edit="openEdit"
          @pagar="openPago"
          @detalles="openDetalles"
          @cambiar-estado="cambiarEstado"
          @eliminar="eliminarOrden"
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
        <FormSection label="Cliente">
          <ComboSelect v-model="form.cliente_id" label="Cliente" placeholder="Buscar cliente por nombre..." :options="clienteOptions" required />
          <button
            type="button"
            class="text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400"
            @click="toggleNewCliente"
          >
            {{ showNewCliente ? 'Cancelar' : '+ El cliente no existe, crearlo' }}
          </button>

          <div v-if="showNewCliente" class="grid gap-3 rounded-lg border border-slate-200 bg-white p-3 sm:grid-cols-2 dark:border-slate-800 dark:bg-slate-900">
            <BaseInput v-model="newCliente.nombre" label="Nombre del cliente" placeholder="Nombre completo" required />
            <BaseInput v-model="newCliente.telefono" label="Telefono" />
            <div class="sm:col-span-2 flex justify-end">
              <BaseButton type="button" size="sm" :loading="savingCliente" @click="saveNewCliente">Guardar cliente</BaseButton>
            </div>
          </div>
        </FormSection>

        <FormSection label="Equipo">
          <div class="grid gap-4 sm:grid-cols-3">
            <BaseInput v-model="form.equipo" label="Equipo" placeholder="Celular, tablet..." required />
            <BaseInput v-model="form.marca" label="Marca" />
            <BaseInput v-model="form.modelo" label="Modelo" />
          </div>
          <BaseInput v-model="form.problema" label="Falla reportada" textarea required />
        </FormSection>

        <FormSection label="Estado y fecha">
          <div class="grid gap-4 sm:grid-cols-3">
            <BaseInput v-model="form.numero_orden" label="Numero de orden" readonly :hint="editingId ? '' : 'Consecutivo automático'" />
            <BaseInput v-model="form.estado" label="Estado" type="select">
              <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
            </BaseInput>
            <BaseInput v-model="form.fecha_ingreso" label="Fecha de ingreso" type="datetime-local" />
          </div>
        </FormSection>

        <FormSection label="Valores">
          <div class="grid gap-4 sm:grid-cols-2">
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
        </FormSection>

        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="modalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="saving">{{ editingId ? 'Actualizar' : 'Crear orden' }}</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Registrar pago -->
    <BaseModal v-model="pagoModalOpen" title="Registrar pago" :subtitle="pagoTarget ? `Orden #${pagoTarget.id} · ${clienteNombre(pagoTarget)}` : ''">
      <form class="grid gap-4" @submit.prevent="savePago">
        <div class="grid gap-4 sm:grid-cols-3">
          <BaseInput v-model="pagoForm.valor" label="Valor" type="number" required />
          <BaseInput v-model="pagoForm.metodo_pago" label="Metodo de pago" type="select">
            <option value="Efectivo">Efectivo</option>
            <option value="Transferencia">Transferencia</option>
            <option value="Nequi">Nequi</option>
            <option value="Daviplata">Daviplata</option>
            <option value="Tarjeta">Tarjeta</option>
          </BaseInput>
          <BaseInput v-model="pagoForm.fecha" label="Fecha y hora" type="datetime-local" required />
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
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseSelect from '../components/BaseSelect.vue'
import SearchField from '../components/SearchField.vue'
import ComboSelect from '../components/ComboSelect.vue'
import EmptyState from '../components/EmptyState.vue'
import FabButton from '../components/FabButton.vue'
import FilterBar from '../components/FilterBar.vue'
import DateRangePicker from '../components/DateRangePicker.vue'
import FormSection from '../components/FormSection.vue'
import OrderCard from '../components/OrderCard.vue'
import PageHeader from '../components/PageHeader.vue'
import Paginator from '../components/Paginator.vue'
import { ESTADOS_LABELS } from '../constants/estados'
import { clientesApi, ordenesApi, pagosApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'
import { useUiStore } from '../stores/ui'
import { normalizarTexto } from '../utils/texto'

const route = useRoute()
const router = useRouter()
const { formatCurrency, parseUTC } = useFormatters()
const { loading, run } = useApiState()
const ui = useUiStore()
const initialLoading = ref(true)
const ordenes = ref([])
const clientes = ref([])
const now = new Date()

import { toISO } from '../utils/dateRanges'

const dateRange = ref({ desde: '', hasta: '' })

const search = ref(typeof route.query.q === 'string' ? route.query.q : '')
const statusFilter = ref(search.value ? '' : 'Pendiente')
const modalOpen = ref(false)
const saving = ref(false)
const editingId = ref(null)
const estados = ESTADOS_LABELS

const showNewCliente = ref(false)
const savingCliente = ref(false)
const newCliente = reactive({ nombre: '', telefono: '' })

// Fecha local actual formateada para input datetime-local (YYYY-MM-DDTHH:mm)
function localNow() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}T${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const form = reactive({ cliente_id: '', numero_orden: '', equipo: '', marca: '', modelo: '', problema: '', estado: 'Pendiente', valor: 0, saldo: 0, abono: 0, abono_metodo_pago: 'Efectivo', fecha_ingreso: localNow() })

// Mapa id->cliente, se recalcula solo cuando cambia la lista de
// clientes (no en cada letra tipeada). Con ~2300 clientes y ~3500
// ordenes, clienteNombre() buscando con .find() adentro del filtro de
// busqueda hacia hasta ~8 millones de comparaciones por tecla -- de ahi
// la demora. Con el Map la busqueda de cada orden es O(1).
const clientesPorId = computed(() => {
  const map = new Map()
  for (const cliente of clientes.value) {
    map.set(Number(cliente.id), cliente)
  }
  return map
})

// Opciones para el buscador de cliente del formulario "Nueva orden".
// Se recalcula solo cuando cambia la lista de clientes, no en cada
// letra tipeada dentro del combobox (ese filtro lo hace ComboSelect
// internamente sobre este arreglo ya armado).
const clienteOptions = computed(() =>
  clientes.value.map((cliente) => ({
    value: cliente.id,
    label: cliente.nombre || cliente.name || `Cliente ${cliente.id}`,
    sublabel: cliente.telefono || '',
  })),
)

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
const pagoForm = reactive({ valor: 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '', fecha: localNow() })

// Valor numerico del numero_orden para ordenar de mayor a menor. Los
// numeros de orden son strings de digitos (ej. "17761"); las ordenes
// sin numero (dato legacy) caen al final.
function numeroOrdenValor(orden) {
  const n = parseInt(orden.numero_orden, 10)
  return Number.isNaN(n) ? -Infinity : n
}

const filteredOrdenes = computed(() => {
  const term = normalizarTexto(search.value)
  return ordenes.value.filter((orden) => {
    const matchesSearch = !term || (
      normalizarTexto(orden.equipo).includes(term)
      || normalizarTexto(orden.marca).includes(term)
      || normalizarTexto(orden.modelo).includes(term)
      || normalizarTexto(orden.problema).includes(term)
      || normalizarTexto(orden.estado).includes(term)
      || normalizarTexto(orden.numero_orden).includes(term)
      || normalizarTexto(clienteNombre(orden)).includes(term)
    )
    const matchesStatus = !statusFilter.value || orden.estado === statusFilter.value

    const fecha = orden.fecha_ingreso ? parseUTC(orden.fecha_ingreso) : null
    if (!fecha) return false

    const fechaISO = toISO(fecha)
    const matchesDate = (!dateRange.value.desde && !dateRange.value.hasta)
      || (dateRange.value.desde && dateRange.value.hasta && fechaISO >= dateRange.value.desde && fechaISO <= dateRange.value.hasta)
      || (dateRange.value.desde && !dateRange.value.hasta && fechaISO === dateRange.value.desde)

    return matchesSearch && matchesStatus && matchesDate
  }).sort((a, b) => numeroOrdenValor(b) - numeroOrdenValor(a))
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
  const cliente = clientesPorId.value.get(Number(orden.cliente_id))
  return cliente?.nombre || cliente?.name || orden.cliente_nombre || `Cliente ${orden.cliente_id || '-'}`
}

function resetForm() {
  Object.assign(form, { cliente_id: '', numero_orden: '', equipo: '', marca: '', modelo: '', problema: '', estado: 'Pendiente', valor: 0, saldo: 0, abono: 0, abono_metodo_pago: 'Efectivo', fecha_ingreso: localNow() })
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

async function openCreate() {
  resetForm()
  modalOpen.value = true
  // Cargar el siguiente número de orden para mostrarlo antes de guardar
  try {
    const res = await ordenesApi.siguienteNumero()
    form.numero_orden = res.data.numero_orden
  } catch {
    form.numero_orden = '—'
  }
}

function openEdit(orden) {
  editingId.value = orden.id
  // Convertir fecha_ingreso ISO a formato datetime-local (YYYY-MM-DDTHH:mm)
  let fechaLocal = localNow()
  if (orden.fecha_ingreso) {
    const d = new Date(orden.fecha_ingreso)
    fechaLocal = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}T${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  }
  Object.assign(form, {
    cliente_id: orden.cliente_id || orden.cliente?.id || '',
    numero_orden: orden.numero_orden || '',
    equipo: orden.equipo || '',
    marca: orden.marca || '',
    modelo: orden.modelo || '',
    problema: orden.problema || '',
    estado: orden.estado || 'Pendiente',
    valor: orden.valor || 0,
    saldo: orden.saldo || 0,
    abono: 0,
    abono_metodo_pago: 'Efectivo',
    fecha_ingreso: fechaLocal,
  })
  modalOpen.value = true
}

function openPago(orden) {
  pagoTarget.value = orden
  Object.assign(pagoForm, { valor: orden.saldo || 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '', fecha: localNow() })
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
  // Convertir fecha_ingreso de datetime-local a ISO para el backend
  const fechaISO = form.fecha_ingreso ? new Date(form.fecha_ingreso).toISOString() : null
  const payload = {
    ...ordenFields,
    cliente_id: Number(form.cliente_id),
    valor: valorNum,
    fecha_ingreso: fechaISO,
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
          created_at: fechaISO,
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
  const fechaISO = pagoForm.fecha ? new Date(pagoForm.fecha).toISOString() : null

  try {
    await run(() => pagosApi.create({
      ...pagoForm,
      orden_id: pagoTarget.value.id,
      valor: Number(pagoForm.valor || 0),
      created_at: fechaISO,
    }), 'Pago registrado')
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
      fecha_ingreso: orden.fecha_ingreso || null,
    }),
    'Estado actualizado',
  )
  await loadData()
}

async function eliminarOrden(orden) {
  const confirmed = await ui.confirm({
    title: `Eliminar orden #${orden.numero_orden || orden.id}`,
    message: `Se eliminará la orden de "${orden.equipo || 'Equipo'}" junto con todos sus pagos, historial de estados y repuestos asociados. Esta acción no se puede deshacer.`,
  })
  if (!confirmed) return
  await run(() => ordenesApi.remove(orden.id), 'Orden eliminada')
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
