<template>
  <BaseCard title="Alertas" subtitle="Se calculan solas, nada escrito a mano" content-class="p-4">
    <div v-if="alerts.length" class="space-y-2.5">
      <component
        :is="tieneDetalle(alert) ? 'button' : 'div'"
        v-for="alert in alerts"
        :key="alert.tipo"
        :type="tieneDetalle(alert) ? 'button' : undefined"
        class="flex w-full items-start gap-3 rounded-xl border p-3 text-left"
        :class="[
          severityClasses[alert.severidad].border,
          tieneDetalle(alert) ? 'cursor-pointer transition hover:shadow-sm hover:brightness-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-400' : '',
        ]"
        @click="tieneDetalle(alert) && abrirDetalle(alert)"
      >
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg" :class="severityClasses[alert.severidad].iconBg">
          <AppIcon name="alert" class="h-4 w-4" :class="severityClasses[alert.severidad].iconColor" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center justify-between gap-2">
            <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">{{ alert.titulo }}</p>
            <span v-if="alert.monto" class="shrink-0 text-sm font-semibold text-slate-950 dark:text-white">{{ formatCurrency(alert.monto) }}</span>
          </div>
          <p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{{ alert.mensaje }}</p>
          <p v-if="tieneDetalle(alert)" class="mt-1 text-xs font-medium text-slate-400 dark:text-slate-500">Click para ver el detalle</p>
        </div>
        <AppIcon v-if="tieneDetalle(alert)" name="chevron-right" class="mt-1.5 h-4 w-4 shrink-0 text-slate-400" />
      </component>
    </div>
    <EmptyState v-else icon="check" title="Todo en orden" description="No hay alertas activas para este periodo." />
  </BaseCard>

  <!-- Popup de detalle: ordenes detras de la alerta -->
  <BaseModal v-model="modalAbierto" :title="alertaActiva?.titulo || ''" :subtitle="subtituloModal">
    <div v-if="cargando" class="py-10 text-center text-sm text-slate-500 dark:text-slate-400">Cargando...</div>
    <EmptyState v-else-if="!items.length" icon="check" title="Sin registros" description="No hay ordenes en esta alerta." />
    <template v-else>
      <input
        v-model="busqueda"
        type="search"
        placeholder="Buscar por orden, cliente, telefono o equipo..."
        class="mb-3 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-slate-400 dark:border-slate-800 dark:bg-slate-900 dark:text-white"
      />
      <ul class="divide-y divide-slate-100 dark:divide-slate-800">
        <li v-for="item in itemsFiltrados" :key="item.id">
          <button
            type="button"
            class="flex w-full items-center gap-3 rounded-lg px-2 py-3 text-left transition hover:bg-slate-50 dark:hover:bg-slate-900"
            @click="irAOrden(item)"
          >
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <span class="text-sm font-semibold text-slate-950 dark:text-white">{{ item.numero_orden || `#${item.id}` }}</span>
                <StatusBadge :value="item.estado" />
              </div>
              <p class="mt-0.5 truncate text-sm text-slate-600 dark:text-slate-300">
                {{ item.cliente_nombre || 'Sin cliente' }}<span v-if="item.cliente_telefono"> · {{ item.cliente_telefono }}</span>
              </p>
              <p class="truncate text-xs text-slate-500 dark:text-slate-400">
                {{ descripcionEquipo(item) }} · Ingreso {{ formatDate(item.fecha_ingreso) }}
              </p>
            </div>
            <div class="shrink-0 text-right">
              <template v-if="alertaActiva?.tipo === 'cartera_vencida'">
                <p class="text-sm font-semibold text-red-600 dark:text-red-400">{{ formatCurrency(item.saldo) }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400">de {{ formatCurrency(item.valor) }}</p>
              </template>
              <template v-else>
                <p class="text-sm font-semibold text-red-600 dark:text-red-400">{{ item.dias }} dias</p>
                <p class="text-xs text-slate-500 dark:text-slate-400">sin movimiento</p>
              </template>
            </div>
            <AppIcon name="chevron-right" class="h-4 w-4 shrink-0 text-slate-400" />
          </button>
        </li>
      </ul>
      <p v-if="!itemsFiltrados.length" class="py-6 text-center text-sm text-slate-500 dark:text-slate-400">Ninguna orden coincide con la busqueda.</p>
    </template>
  </BaseModal>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '../AppIcon.vue'
import BaseCard from '../BaseCard.vue'
import BaseModal from '../BaseModal.vue'
import EmptyState from '../EmptyState.vue'
import StatusBadge from '../StatusBadge.vue'
import { dashboardApi } from '../../api/resources'
import { useApiState } from '../../composables/useApiState'
import { useFormatters } from '../../composables/useFormatters'

defineProps({
  alerts: { type: Array, required: true }, // [{tipo, severidad, titulo, mensaje, cantidad, monto}]
})

const { formatCurrency, formatDate } = useFormatters()
const { run } = useApiState()
const router = useRouter()

// Solo estas alertas tienen popup de detalle (ver ALERTAS_CON_DETALLE en
// backend/app/services/dashboard_service.py).
const TIPOS_CON_DETALLE = ['sin_movimiento', 'cartera_vencida']

const modalAbierto = ref(false)
const alertaActiva = ref(null)
const items = ref([])
const cargando = ref(false)
const busqueda = ref('')

function tieneDetalle(alert) {
  return TIPOS_CON_DETALLE.includes(alert.tipo)
}

const subtituloModal = computed(() => {
  if (!alertaActiva.value || cargando.value) return ''
  const total = items.value.length
  if (alertaActiva.value.tipo === 'cartera_vencida') {
    const saldo = items.value.reduce((acc, item) => acc + Number(item.saldo || 0), 0)
    return `${total} orden(es) · ${formatCurrency(saldo)} pendiente por cobrar`
  }
  return `${total} equipo(s) ordenados por dias sin movimiento`
})

const itemsFiltrados = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  if (!q) return items.value
  return items.value.filter((item) =>
    [item.numero_orden, item.cliente_nombre, item.cliente_telefono, item.equipo, item.marca, item.modelo]
      .some((campo) => String(campo || '').toLowerCase().includes(q)),
  )
})

function descripcionEquipo(item) {
  return [item.equipo, item.marca, item.modelo].filter(Boolean).join(' ') || 'Equipo sin descripcion'
}

async function abrirDetalle(alert) {
  alertaActiva.value = alert
  items.value = []
  busqueda.value = ''
  modalAbierto.value = true
  cargando.value = true
  try {
    const response = await run(() => dashboardApi.alertaDetalle(alert.tipo))
    items.value = response.data
  } catch {
    modalAbierto.value = false
  } finally {
    cargando.value = false
  }
}

function irAOrden(item) {
  modalAbierto.value = false
  router.push({ name: 'orden-detalle', params: { id: item.id } })
}

const severityClasses = {
  alta: {
    border: 'border-red-200 bg-red-50/60 dark:border-red-500/20 dark:bg-red-500/5',
    iconBg: 'bg-red-100 dark:bg-red-500/15',
    iconColor: 'text-red-600 dark:text-red-400',
  },
  media: {
    border: 'border-orange-200 bg-orange-50/60 dark:border-orange-500/20 dark:bg-orange-500/5',
    iconBg: 'bg-orange-100 dark:bg-orange-500/15',
    iconColor: 'text-orange-600 dark:text-orange-400',
  },
  baja: {
    border: 'border-slate-200 bg-slate-50/60 dark:border-slate-800 dark:bg-slate-900/40',
    iconBg: 'bg-slate-100 dark:bg-slate-800',
    iconColor: 'text-slate-600 dark:text-slate-300',
  },
}
</script>
