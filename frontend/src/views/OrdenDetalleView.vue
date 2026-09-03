<template>
  <div class="space-y-6">
    <BaseCard v-if="notFound" content-class="p-6">
      <EmptyState icon="orders" title="Orden no encontrada" description="Puede que la orden haya sido eliminada." />
      <div class="mt-4 flex justify-center">
        <BaseButton variant="secondary" @click="router.push({ name: 'ordenes' })">Volver a ordenes</BaseButton>
      </div>
    </BaseCard>

    <template v-else-if="orden">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div class="flex min-w-0 items-start gap-4">
          <button type="button" class="mt-1 shrink-0 rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900" title="Volver" @click="router.push({ name: 'ordenes' })">
            <AppIcon name="chevron-left" />
          </button>
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300">
            <AppIcon name="wrench" />
          </div>
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <span class="font-mono text-sm text-slate-400">ORD-{{ orden.id }}</span>
              <StatusBadge :value="orden.estado" />
            </div>
            <h1 class="mt-0.5 break-words text-xl font-semibold leading-snug tracking-tight text-slate-950 dark:text-white">
              {{ orden.equipo || 'Equipo' }}
            </h1>
            <p class="mt-1 truncate text-sm text-slate-500 dark:text-slate-400">
              <RouterLink v-if="orden.cliente_id" :to="{ name: 'cliente-detalle', params: { id: orden.cliente_id } }" class="hover:underline">{{ clienteNombre }}</RouterLink>
              <span v-else>{{ clienteNombre }}</span>
              · {{ orden.marca || 'Sin marca' }}{{ orden.modelo ? ` ${orden.modelo}` : '' }}
            </p>
          </div>
        </div>

        <div class="flex shrink-0 flex-wrap items-center gap-2">
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
        <StatCard label="Dias en taller" :value="diasEnTaller === null ? '-' : `${diasEnTaller} dias`" icon="clock" tone="purple" />
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
      <section v-if="activeTab === 'resumen'">
        <BaseCard title="Falla reportada" subtitle="Descripcion entregada por el cliente">
          <p class="rounded-lg bg-slate-50 p-3 text-sm text-slate-700 dark:bg-slate-900 dark:text-slate-200">{{ orden.problema || 'Sin descripcion' }}</p>
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

      <!-- Repuestos -->
      <section v-if="activeTab === 'repuestos'">
        <BaseCard title="Repuestos usados" subtitle="Repuestos consumidos del inventario para esta orden">
          <template #header>
            <BaseButton size="sm" icon="plus" @click="openAgregarRepuesto">Agregar repuesto</BaseButton>
          </template>

          <div v-if="repuestosUsados.length" class="divide-y divide-slate-100 dark:divide-slate-800">
            <div v-for="repuesto in repuestosUsados" :key="repuesto.id" class="flex items-center justify-between gap-3 py-3 first:pt-0 last:pb-0">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">{{ repuesto.producto?.nombre || 'Producto' }}</p>
                <p class="truncate text-xs text-slate-500 dark:text-slate-400">Cantidad: {{ repuesto.cantidad }} · Precio unitario: {{ formatCurrency(repuesto.precio_venta) }}</p>
              </div>
              <div class="flex items-center gap-2">
                <span class="shrink-0 text-sm font-bold text-slate-900 dark:text-white">{{ formatCurrency(repuesto.cantidad * repuesto.precio_venta) }}</span>
                <BaseButton variant="ghost" size="sm" icon="trash" @click="removeRepuesto(repuesto)">Eliminar</BaseButton>
              </div>
            </div>
          </div>
          <EmptyState v-else icon="wrench" title="Sin repuestos" description="No hay repuestos registrados para esta orden." />
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
        <div class="grid gap-4 sm:grid-cols-3">
          <BaseInput v-model="editForm.numero_orden" label="Numero de orden" readonly />
          <BaseInput v-model="editForm.estado" label="Estado" type="select">
            <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
          </BaseInput>
          <BaseInput v-model="editForm.fecha_ingreso" label="Fecha de ingreso" type="datetime-local" />
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

    <!-- Agregar Repuesto -->
    <BaseModal v-model="repuestoModalOpen" title="Agregar repuesto" subtitle="Añadir un repuesto del inventario a la orden de reparación.">
      <form class="grid gap-4" @submit.prevent="saveRepuesto">
        <ComboSelect v-model="repuestoForm.producto_id" label="Repuesto / Producto" :options="productosOptions" required />
        <div class="grid gap-4 grid-cols-2">
          <BaseInput v-model="repuestoForm.cantidad" label="Cantidad" type="number" required min="1" />
          <BaseInput v-model="repuestoForm.precio_venta" label="Precio Unitario" type="number" required />
        </div>
        <div class="text-xs text-slate-500" v-if="selectedProducto">
          Stock actual: <span class="font-bold">{{ selectedProducto.stock_actual }}</span>
        </div>
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="repuestoModalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="savingRepuesto">Guardar repuesto</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseModal from '../components/BaseModal.vue'
import ComboSelect from '../components/ComboSelect.vue'
import EmptyState from '../components/EmptyState.vue'
import StatCard from '../components/StatCard.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { clientesApi, ordenesApi, pagosApi, inventarioApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { ESTADOS_LABELS, resolveEstado } from '../constants/estados'
import { useFormatters } from '../composables/useFormatters'
import { useUiStore } from '../stores/ui'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const router = useRouter()
const { formatCurrency, formatDate } = useFormatters()
const { run } = useApiState()

const ui = useUiStore()
const estados = ESTADOS_LABELS
const tabs = [
  { key: 'resumen', label: 'Resumen' },
  { key: 'pagos', label: 'Pagos' },
  { key: 'timeline', label: 'Linea de tiempo' },
  { key: 'repuestos', label: 'Repuestos' },
]

const orden = ref(null)
const clientes = ref([])
const pagos = ref([])
const historialEstados = ref([])
const notFound = ref(false)
const activeTab = ref('resumen')

const cambiandoEstado = ref(false)
const cambiandoEstadoGuardando = ref(false)
const nuevoEstado = ref('')

const editModalOpen = ref(false)
const savingEdit = ref(false)
const editForm = reactive({ cliente_id: '', numero_orden: '', equipo: '', marca: '', modelo: '', problema: '', diagnostico: '', estado: 'Pendiente', valor: 0, saldo: 0, fecha_ingreso: '' })

const pagoModalOpen = ref(false)
const savingPago = ref(false)
const pagoForm = reactive({ valor: 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '' })

// --- Repuestos ---
const repuestosUsados = ref([])
const repuestoModalOpen = ref(false)
const savingRepuesto = ref(false)
const repuestoForm = reactive({ producto_id: '', cantidad: 1, precio_venta: 0 })
const productosInventario = ref([])

const productosOptions = computed(() =>
  productosInventario.value
    .filter(p => p.stock_actual > 0)
    .map(p => ({ value: p.id, label: `${p.nombre}${p.codigo_sku ? ` (${p.codigo_sku})` : ''} — Stock: ${p.stock_actual}` }))
)

const selectedProducto = computed(() =>
  productosInventario.value.find(p => Number(p.id) === Number(repuestoForm.producto_id)) || null
)

// Actualizar precio de venta al seleccionar un producto
watch(() => repuestoForm.producto_id, (nuevoId) => {
  const prod = productosInventario.value.find(p => Number(p.id) === Number(nuevoId))
  if (prod) repuestoForm.precio_venta = prod.precio_venta || 0
})

// --- Funciones de repuestos ---
async function loadRepuestos() {
  const res = await ordenesApi.listRepuestos(props.id)
  repuestosUsados.value = res.data
}

async function loadProductos() {
  const res = await inventarioApi.listProductos()
  productosInventario.value = res.data
}

function openAgregarRepuesto() {
  repuestoForm.producto_id = ''
  repuestoForm.cantidad = 1
  repuestoForm.precio_venta = 0
  repuestoModalOpen.value = true
}

async function saveRepuesto() {
  savingRepuesto.value = true
  try {
    await run(() => ordenesApi.addRepuesto(props.id, {
      producto_id: Number(repuestoForm.producto_id),
      cantidad: Number(repuestoForm.cantidad),
      precio_venta: Number(repuestoForm.precio_venta),
    }), 'Repuesto agregado')
    repuestoModalOpen.value = false
    await Promise.all([loadRepuestos(), loadProductos()])
  } finally {
    savingRepuesto.value = false
  }
}

async function removeRepuesto(repuesto) {
  const confirmed = await ui.confirm({
    title: `Eliminar repuesto "${repuesto.producto?.nombre || 'Producto'}"`,
    message: 'Se devolverá el stock al inventario.',
  })
  if (!confirmed) return
  await run(() => ordenesApi.removeRepuesto(props.id, repuesto.id), 'Repuesto eliminado')
  await Promise.all([loadRepuestos(), loadProductos()])
}

const clienteNombre = computed(() => {
  if (!orden.value) return 'Cliente'
  const cliente = clientes.value.find((item) => Number(item.id) === Number(orden.value.cliente_id))
  return cliente?.nombre || cliente?.name || `Cliente ${orden.value.cliente_id || '-'}`
})

// Igual que en OrderCard.vue: con fecha de entrega, es la duracion real
// de la reparacion; sin ella, cuenta hasta hoy si sigue activa, o
// muestra null (dato desconocido) si ya esta entregada/cancelada pero
// sin fecha registrada (import historico).
const diasEnTaller = computed(() => {
  if (!orden.value?.fecha_ingreso) return null
  if (orden.value.fecha_entrega) {
    const ms = new Date(orden.value.fecha_entrega).getTime() - new Date(orden.value.fecha_ingreso).getTime()
    return Math.max(Math.floor(ms / 86_400_000), 0)
  }
  const estado = (orden.value.estado || '').toLowerCase()
  if (estado.includes('entreg') || estado.includes('cancel')) return null
  const ms = Date.now() - new Date(orden.value.fecha_ingreso).getTime()
  return Math.max(Math.floor(ms / 86_400_000), 0)
})

const pagosOrden = computed(() => {
  if (!orden.value) return []
  return pagos.value
    .filter((pago) => Number(pago.orden_id) === Number(orden.value.id))
    .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
})

// Traza real de la orden: ingreso, pagos (marcando aparte el abono
// inicial de "Nueva orden") y cada cambio de estado real (pendiente ->
// listo -> entregado, o cancelado), tomado de historial_estados. Nada
// inventado -- una orden vieja, cargada antes de este historial existir,
// simplemente muestra menos eventos.
const ABONO_INICIAL_MARCA = 'Abono inicial al crear la orden'

const timelineEvents = computed(() => {
  if (!orden.value) return []
  const events = [
    { id: 'creada', label: 'Orden creada', detail: `${orden.value.equipo || 'Equipo'} ingreso al taller`, date: orden.value.fecha_ingreso, icon: 'orders' },
  ]

  pagosOrden.value.forEach((pago) => {
    const esAbonoInicial = pago.observaciones === ABONO_INICIAL_MARCA
    events.push({
      id: `pago-${pago.id}`,
      label: esAbonoInicial ? 'Abono inicial registrado' : 'Pago registrado',
      detail: `${formatCurrency(pago.valor)} · ${pago.metodo_pago || 'Sin metodo'}`,
      date: pago.created_at,
      icon: 'payments',
    })
  })

  historialEstados.value.forEach((cambio) => {
    events.push({
      id: `estado-${cambio.id}`,
      label: `Cambio de estado: ${cambio.estado_nuevo || '-'}`,
      detail: cambio.estado_anterior ? `Antes: ${cambio.estado_anterior}` : 'Primer estado registrado',
      date: cambio.created_at,
      icon: resolveEstado(cambio.estado_nuevo).icon,
    })
  })

  // Fallback para ordenes viejas, importadas antes de que existiera el
  // historial de estados: si tienen fecha_entrega pero ningun cambio de
  // estado a "Entregado" en el historial, se agrega igual (dato real,
  // solo que no vino del flujo de "Cambiar estado").
  const yaTieneEntregaEnHistorial = historialEstados.value.some((c) => resolveEstado(c.estado_nuevo).key === 'entregado')
  if (orden.value.fecha_entrega && !yaTieneEntregaEnHistorial) {
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
    await Promise.all([loadOrden(), loadHistorial()])
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
    fecha_ingreso: source.fecha_ingreso || null,
  }
}

// Fecha local actual formateada para input datetime-local (YYYY-MM-DDTHH:mm)
function localNow() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}T${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function isoToLocal(isoStr) {
  if (!isoStr) return localNow()
  const d = new Date(isoStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}T${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function openEdit() {
  Object.assign(editForm, {
    cliente_id: orden.value.cliente_id || '',
    numero_orden: orden.value.numero_orden || '',
    equipo: orden.value.equipo || '',
    marca: orden.value.marca || '',
    modelo: orden.value.modelo || '',
    problema: orden.value.problema || '',
    diagnostico: orden.value.diagnostico || '',
    estado: orden.value.estado || 'Pendiente',
    valor: orden.value.valor || 0,
    saldo: orden.value.saldo || 0,
    fecha_ingreso: isoToLocal(orden.value.fecha_ingreso),
  })
  editModalOpen.value = true
}

async function saveEdit() {
  savingEdit.value = true
  const fechaISO = editForm.fecha_ingreso ? new Date(editForm.fecha_ingreso).toISOString() : null
  const payload = { ...editForm, cliente_id: Number(editForm.cliente_id), valor: Number(editForm.valor || 0), saldo: Number(editForm.saldo || 0), fecha_ingreso: fechaISO }
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

async function loadHistorial() {
  const response = await ordenesApi.historial(props.id)
  historialEstados.value = response.data
}

onMounted(async () => {
  // Solo una orden que de verdad no existe (o no carga) debe mostrar
  // "Orden no encontrada". Antes, si clientes/pagos/historial fallaban
  // por cualquier motivo (una API caida, una ruta vieja, lo que sea),
  // el catch de abajo tapaba una orden real con ese mensaje -- muy
  // confuso, porque la orden si existia.
  try {
    await loadOrden()
  } catch {
    notFound.value = true
    return
  }

  const [clientesResult] = await Promise.allSettled([run(() => clientesApi.list()), loadPagos(), loadHistorial(), loadRepuestos(), loadProductos()])
  if (clientesResult.status === 'fulfilled') {
    clientes.value = clientesResult.value.data
  }
})
</script>
