<template>
  <div class="space-y-6">
    <PageHeader title="Ingresos" subtitle="Pagos de ordenes y ventas de mostrador (pilas, accesorios, servicios rapidos), todo en un solo lugar.">
      <template #actions>
        <div class="flex items-center gap-2">
           <select v-model="selectedMonth" class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
             <option :value="null">Todos los meses</option>
             <option v-for="(mes, index) in meses" :key="mes" :value="index + 1">{{ mes }}</option>
           </select>
           <select v-if="selectedMonth !== null" v-model="selectedDay" class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
             <option :value="null">Todos los días</option>
             <option v-for="d in daysInSelectedMonth" :key="d" :value="d">{{ d }}</option>
           </select>
           <select v-model="selectedYear" class="h-10 rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium text-slate-700 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200">
             <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
           </select>
           <BaseButton icon="plus" @click="openCreate">Nuevo ingreso</BaseButton>
        </div>
      </template>
    </PageHeader>

    <FabButton label="Registrar ingreso" @click="openCreate" />

    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Total ingresos" :value="formatCurrency(summary.total)" icon="trend-up" tone="green" hint="Segun los filtros aplicados" />
      <StatCard label="Ingreso promedio" :value="formatCurrency(summary.promedio)" icon="dashboard" tone="slate" hint="Promedio por movimiento" />
      <StatCard label="De ordenes" :value="formatNumber(summary.deOrdenes)" icon="payments" tone="teal" hint="Pagos asociados a una orden" />
      <StatCard label="Movimientos" :value="formatNumber(filteredRows.length)" icon="orders" tone="sky" hint="Registros de ingreso" />
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <BaseCard title="Ingresos por metodo" subtitle="Distribucion de entradas segun la forma de pago">
        <div class="space-y-5">
          <div v-for="item in methodBars" :key="item.label">
            <div class="mb-2 flex items-center justify-between text-sm">
              <span class="font-medium capitalize text-slate-700 dark:text-slate-200">{{ item.label }}</span>
              <span class="text-slate-500 dark:text-slate-400">{{ formatCurrency(item.value) }}</span>
            </div>
            <div class="h-4 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div class="h-full rounded-full bg-slate-950 transition-all dark:bg-white" :style="{ width: `${item.percent}%` }" />
            </div>
          </div>
        </div>
        <EmptyState v-if="!methodBars.length" icon="cash" title="Sin ingresos" description="Registra pagos o ventas para visualizar los ingresos por metodo de pago." />
      </BaseCard>

      <BaseCard title="Ingresos por origen" subtitle="De ordenes de reparacion vs. otras categorias">
        <div v-if="origenBars.length" class="space-y-4">
          <div v-for="item in origenBars" :key="item.categoria">
            <div class="mb-2 flex items-center justify-between gap-4 text-sm">
              <span class="font-medium capitalize text-slate-700 dark:text-slate-200">{{ item.label }}</span>
              <span class="text-slate-500 dark:text-slate-400">{{ formatCurrency(item.total) }}</span>
            </div>
            <div class="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div class="h-full rounded-full bg-emerald-500" :style="{ width: `${item.percent}%` }" />
            </div>
          </div>
        </div>
        <EmptyState v-else icon="cash" title="Sin ingresos" description="Los ingresos por origen apareceran cuando registres pagos o ventas." />
      </BaseCard>
    </div>

    <BaseCard title="Historial de ingresos" subtitle="Pagos de ordenes y ventas sin factura, con trazabilidad" content-class="p-4">
      <div class="mb-4 grid gap-3 lg:grid-cols-[1fr_190px]">
        <label class="relative block">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-2.5 text-slate-400" />
          <input v-model="filters.search" class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950" placeholder="Buscar por orden, referencia, metodo o categoria" />
        </label>
        <BaseInput v-model="filters.origen" type="select">
          <option value="">Todos los origenes</option>
          <option value="orden">De ordenes</option>
          <option v-for="cat in categoriasIngreso" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
        </BaseInput>
      </div>

      <BaseTable :columns="columns" :rows="filteredRows" :loading="loading">
        <template #origen="{ row }">
          <RouterLink v-if="row.source === 'pago'" :to="{ name: 'orden-detalle', params: { id: row.raw.orden_id } }" class="font-mono text-brand-600 hover:underline dark:text-brand-400">
            {{ row.origenLabel }}
          </RouterLink>
          <span v-else class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-slate-700 dark:bg-slate-800 dark:text-slate-200">{{ row.origenLabel }}</span>
          <span v-if="row.origenSub" class="ml-1.5 text-xs text-slate-500 dark:text-slate-400">{{ row.origenSub }}</span>
        </template>
        <template #valor="{ row }">{{ formatCurrency(row.valor) }}</template>
        <template #metodo_pago="{ row }">
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-slate-700 dark:bg-slate-800 dark:text-slate-200">{{ row.metodo_pago }}</span>
        </template>
        <template #detalle="{ row }">{{ row.detalle }}</template>
        <template #fecha="{ row }">{{ formatDate(row.fecha) }}</template>
        <template #empty>
          <EmptyState icon="payments" title="No hay ingresos" description="Registra pagos de ordenes o ventas de mostrador." />
        </template>
        <template #actions="{ row }">
          <BaseButton variant="ghost" size="sm" icon="trash" @click="removeRow(row)">Eliminar</BaseButton>
        </template>
      </BaseTable>
    </BaseCard>

    <BaseModal v-model="modalOpen" title="Registrar ingreso" subtitle="Un pago de una orden, o una venta / entrada que no requiere orden.">
      <form class="grid gap-4" @submit.prevent="saveIngreso">
        <div class="grid grid-cols-2 gap-2 rounded-lg bg-slate-100 p-1 dark:bg-slate-900">
          <button
            type="button"
            class="rounded-md py-2 text-sm font-medium transition"
            :class="origenTipo === 'orden' ? 'bg-white text-slate-950 shadow-sm dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
            @click="origenTipo = 'orden'"
          >
            De una orden
          </button>
          <button
            type="button"
            class="rounded-md py-2 text-sm font-medium transition"
            :class="origenTipo === 'categoria' ? 'bg-white text-slate-950 shadow-sm dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
            @click="origenTipo = 'categoria'"
          >
            Otra categoria (venta, pila, etc.)
          </button>
        </div>

        <ComboSelect
          v-if="origenTipo === 'orden'"
          v-model="form.orden_id"
          label="Orden"
          placeholder="Buscar orden por numero, equipo o marca..."
          :options="ordenOptions"
          required
        />
        <BaseInput v-else v-model="form.categoria" label="Categoria" type="select" required>
          <option v-for="cat in categoriasIngreso" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
        </BaseInput>

        <div class="grid gap-4 sm:grid-cols-2">
          <BaseInput v-model="form.valor" label="Valor" type="number" required />
          <BaseInput v-model="form.metodo_pago" label="Metodo de pago" type="select">
            <option value="Efectivo">Efectivo</option>
            <option value="Transferencia">Transferencia</option>
            <option value="Nequi">Nequi</option>
            <option value="Daviplata">Daviplata</option>
            <option value="Tarjeta">Tarjeta</option>
            <option value="Otro">Otro</option>
          </BaseInput>
        </div>
        <BaseInput v-if="origenTipo === 'orden'" v-model="form.referencia_pago" label="Referencia" placeholder="Numero de comprobante o nota" />
        <BaseInput v-model="form.observaciones" :label="origenTipo === 'orden' ? 'Observaciones' : 'Descripcion'" :placeholder="origenTipo === 'categoria' ? 'Ej. Venta de pila para iPhone 11' : ''" textarea :required="origenTipo === 'categoria'" />

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
import ComboSelect from '../components/ComboSelect.vue'
import EmptyState from '../components/EmptyState.vue'
import FabButton from '../components/FabButton.vue'
import PageHeader from '../components/PageHeader.vue'
import PeriodFilter from '../components/PeriodFilter.vue'
import StatCard from '../components/StatCard.vue'
import { ordenesApi, pagosApi } from '../api/resources'
import { movimientosCajaApi } from '../api/movimientosCajaApi'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'
import { useUiStore } from '../stores/ui'
import { rangoEsteMes } from '../utils/dateRanges'

const { formatCurrency, formatDate, formatNumber } = useFormatters()
const { loading, run } = useApiState()
const ui = useUiStore()
const route = useRoute()
const router = useRouter()

const pagos = ref([])
const movimientosIngreso = ref([])
const ordenes = ref([])
const modalOpen = ref(false)
const saving = ref(false)
const origenTipo = ref('orden')

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const now = new Date()
const selectedYear = ref(now.getFullYear())
const selectedMonth = ref(now.getMonth() + 1)
const selectedDay = ref(now.getDate())

const filters = reactive({ search: '', origen: '' })
const form = reactive({ orden_id: '', categoria: 'venta', valor: 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '' })

const availableYears = computed(() => {
  const years = new Set([now.getFullYear()])
  unifiedRows.value.forEach(row => {
    if (row.fecha) {
      years.add(new Date(row.fecha).getFullYear())
    }
  })
  return [...years].sort((a, b) => b - a)
})

const daysInSelectedMonth = computed(() => {
  if (!selectedMonth.value) return 0
  return new Date(selectedYear.value, selectedMonth.value, 0).getDate()
})

const categoriasIngreso = [
  { value: 'venta', label: 'Venta' },
  { value: 'accesorio', label: 'Accesorio' },
  { value: 'pila', label: 'Pila' },
  { value: 'servicio_rapido', label: 'Servicio rapido' },
  { value: 'otros', label: 'Otros' },
]
const CATEGORIA_LABELS = Object.fromEntries(categoriasIngreso.map((cat) => [cat.value, cat.label]))

const columns = [
  { key: 'origen', label: 'Origen' },
  { key: 'valor', label: 'Valor' },
  { key: 'metodo_pago', label: 'Metodo' },
  { key: 'detalle', label: 'Detalle' },
  { key: 'fecha', label: 'Fecha' },
]

// Mapa id->orden para mostrar el equipo junto al numero de orden sin
// recorrer el arreglo completo por cada fila (mismo patron que
// OrdenesView.vue con clientes: con ~3500 ordenes, un .find() por fila
// se nota).
const ordenesPorId = computed(() => {
  const map = new Map()
  for (const orden of ordenes.value) {
    map.set(Number(orden.id), orden)
  }
  return map
})

// Opciones del buscador de orden en el modal. Un <select> nativo con
// miles de <option> es lo que hacia que "Registrar ingreso" se sintiera
// trabado al elegir la orden -- ComboSelect solo renderiza los
// resultados que matchean lo tipeado.
const ordenOptions = computed(() =>
  ordenes.value.map((orden) => ({
    value: orden.id,
    label: `ORD-${orden.id} · ${orden.equipo || orden.modelo || 'Orden'}`,
    sublabel: [orden.marca, orden.numero_orden].filter(Boolean).join(' · '),
  })),
)

// Pagos (ligados a una orden) y movimientos de caja tipo "ingreso"
// (ventas de mostrador, pilas, accesorios, servicios rapidos, otros)
// se combinan en una sola tabla con forma comun.
const unifiedRows = computed(() => {
  const pagoRows = pagos.value.map((pago) => {
    const orden = ordenesPorId.value.get(Number(pago.orden_id))
    return {
      source: 'pago',
      id: pago.id,
      origenLabel: `ORD-${pago.orden_id}`,
      origenSub: orden?.equipo || '',
      categoria: 'orden',
      valor: Number(pago.valor || pago.monto || pago.total || 0),
      metodo_pago: pago.metodo_pago || pago.metodo || 'Sin metodo',
      detalle: pago.referencia_pago || pago.observaciones || '-',
      fecha: pago.fecha || pago.created_at,
      raw: pago,
    }
  })

  const ingresoRows = movimientosIngreso.value.map((mov) => ({
    source: 'movimiento',
    id: mov.id,
    origenLabel: CATEGORIA_LABELS[mov.categoria] || mov.categoria || 'Otros',
    origenSub: '',
    categoria: mov.categoria || 'otros',
    valor: Number(mov.valor || 0),
    metodo_pago: mov.metodo_pago || 'Sin metodo',
    detalle: mov.descripcion || '-',
    fecha: mov.created_at,
    raw: mov,
  }))

  return [...pagoRows, ...ingresoRows].sort((a, b) => new Date(b.fecha || 0) - new Date(a.fecha || 0))
})

const filteredRows = computed(() => {
  const term = filters.search.toLowerCase().trim()
  return unifiedRows.value.filter((row) => {
    const matchesSearch = !term || (
      row.origenLabel.toLowerCase().includes(term)
      || row.origenSub.toLowerCase().includes(term)
      || row.detalle.toLowerCase().includes(term)
      || row.metodo_pago.toLowerCase().includes(term)
    )
    const matchesOrigen = !filters.origen || row.categoria === filters.origen

    const fecha = row.fecha ? new Date(row.fecha) : null
    if (!fecha) return false

    const matchesYear = fecha.getFullYear() === selectedYear.value
    const matchesMonth = selectedMonth.value === null || (fecha.getMonth() + 1) === selectedMonth.value
    const matchesDay = selectedDay.value === null || fecha.getDate() === selectedDay.value

    return matchesSearch && matchesOrigen && matchesYear && matchesMonth && matchesDay
  })
})

const summary = computed(() => {
  const valores = filteredRows.value.map((row) => row.valor)
  const total = valores.reduce((sum, valor) => sum + valor, 0)
  return {
    total,
    promedio: valores.length ? total / valores.length : 0,
    deOrdenes: filteredRows.value.filter((row) => row.source === 'pago').length,
  }
})

const methodBars = computed(() => {
  const totals = filteredRows.value.reduce((acc, row) => {
    const method = row.metodo_pago || 'sin metodo'
    acc[method] = (acc[method] || 0) + row.valor
    return acc
  }, {})
  const max = Math.max(...Object.values(totals), 1)
  return Object.entries(totals)
    .map(([label, value]) => ({ label, value, percent: Math.max((value / max) * 100, 6) }))
    .sort((a, b) => b.value - a.value)
})

const origenBars = computed(() => {
  const totals = filteredRows.value.reduce((acc, row) => {
    const key = row.categoria === 'orden' ? 'orden' : (row.categoria || 'otros')
    acc[key] = (acc[key] || 0) + row.valor
    return acc
  }, {})
  const max = Math.max(...Object.values(totals), 1)
  return Object.entries(totals)
    .map(([categoria, total]) => ({
      categoria,
      label: categoria === 'orden' ? 'De ordenes' : (CATEGORIA_LABELS[categoria] || categoria),
      total,
      percent: Math.max((total / max) * 100, 6),
    }))
    .sort((a, b) => b.total - a.total)
})

function resetForm() {
  Object.assign(form, { orden_id: '', categoria: 'venta', valor: 0, metodo_pago: 'Efectivo', referencia_pago: '', observaciones: '' })
}

function openCreate() {
  origenTipo.value = 'orden'
  resetForm()
  modalOpen.value = true
}

async function loadData() {
  const [pagosResponse, movimientosResponse, ordenesResponse] = await Promise.all([
    run(() => pagosApi.list()),
    run(() => movimientosCajaApi.list()),
    run(() => ordenesApi.list()),
  ])
  pagos.value = pagosResponse.data
  movimientosIngreso.value = movimientosResponse.data.filter((mov) => mov.tipo === 'ingreso')
  ordenes.value = ordenesResponse.data
}

async function saveIngreso() {
  saving.value = true

  try {
    if (origenTipo.value === 'orden') {
      await run(() => pagosApi.create({
        orden_id: Number(form.orden_id),
        valor: Number(form.valor || 0),
        metodo_pago: form.metodo_pago,
        referencia_pago: form.referencia_pago,
        observaciones: form.observaciones,
      }), 'Pago registrado')
    } else {
      await run(() => movimientosCajaApi.create({
        tipo: 'ingreso',
        categoria: form.categoria,
        valor: Number(form.valor || 0),
        metodo_pago: form.metodo_pago,
        descripcion: form.observaciones,
      }), 'Ingreso registrado')
    }
    modalOpen.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

async function removeRow(row) {
  const confirmed = await ui.confirm({
    title: `Eliminar ingreso de ${formatCurrency(row.valor)}`,
    message: 'Esta accion no se puede deshacer.',
  })
  if (!confirmed) return

  if (row.source === 'pago') {
    await run(() => pagosApi.remove(row.id), 'Pago eliminado')
  } else {
    await run(() => movimientosCajaApi.remove(row.id), 'Ingreso eliminado')
  }
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
