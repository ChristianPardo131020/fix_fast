<template>
  <BaseCard
    content-class="p-4"
    class="flex flex-col animate-fade-up transition duration-200 hover:-translate-y-1 hover:shadow-lift"
    :style="cardStyle"
  >
    <div class="flex items-center justify-between gap-2">
      <span class="font-mono text-xs font-medium tracking-wide text-slate-400">N° {{ orden.numero_orden || orden.id }}</span>
      <StatusBadge :value="orden.estado || 'recibido'" />
    </div>

    <div class="mt-3">
      <p class="truncate text-sm font-semibold text-slate-950 dark:text-white">{{ clienteNombre }}</p>
      <p class="truncate text-sm text-slate-600 dark:text-slate-300">{{ orden.equipo || orden.modelo || 'Equipo' }}</p>
      <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ orden.marca || 'Sin marca' }}{{ orden.modelo ? ` · ${orden.modelo}` : '' }}</p>
    </div>

    <div class="mt-4 grid grid-cols-3 gap-2 border-t border-slate-100 pt-3 text-xs dark:border-slate-800">
      <div>
        <p class="text-slate-400">Ingreso</p>
        <p class="mt-0.5 font-medium text-slate-700 dark:text-slate-200">{{ formatDate(orden.fecha_ingreso) }}</p>
      </div>
      <div>
        <p class="text-slate-400">En taller</p>
        <p class="mt-0.5 flex flex-wrap items-center gap-1 font-medium text-slate-700 dark:text-slate-200">
          {{ diasEnTaller === null ? '-' : `${diasEnTaller} dias` }}
          <span v-if="prioridad" :class="prioridadClasses" class="rounded-full px-1.5 py-0.5 text-[10px] font-semibold">{{ prioridad.label }}</span>
        </p>
      </div>
      <div>
        <p class="text-slate-400">Saldo</p>
        <p class="mt-0.5 font-semibold text-slate-950 dark:text-white">{{ formatCurrency(orden.saldo) }}</p>
      </div>
    </div>

    <!-- Progreso de pago: acerca visualmente la meta de cobrar la orden
         (Efecto de Tendencia a la Meta + Zeigarnik: lo incompleto se nota). -->
    <div v-if="Number(orden.valor) > 0" class="mt-3">
      <div class="mb-1.5 flex items-center justify-between gap-2 text-xs">
        <span class="font-medium text-slate-400">{{ esPagado ? 'Pagado' : `Pagado ${pctLabel}` }}</span>
        <span class="font-semibold text-slate-700 dark:text-slate-200">
          {{ formatCurrency(abonado) }} <span class="font-normal text-slate-400">/ {{ formatCurrency(orden.valor) }}</span>
        </span>
      </div>
      <div class="h-1.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div class="h-full rounded-full transition-all duration-500" :class="esPagado ? 'bg-green-500' : 'bg-brand-500'" :style="{ width: `${pctPago}%` }" />
      </div>
    </div>

    <div v-if="cambiandoEstado" class="mt-4 flex items-center gap-2">
      <BaseInput v-model="nuevoEstado" type="select" class="flex-1">
        <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
      </BaseInput>
      <BaseButton size="sm" @click="confirmarEstado">Guardar</BaseButton>
      <BaseButton variant="ghost" size="sm" @click="cambiandoEstado = false">Cancelar</BaseButton>
    </div>

    <div class="mt-4 grid grid-cols-2 gap-2 border-t border-slate-100 pt-3 dark:border-slate-800">
      <BaseButton variant="secondary" size="sm" icon="edit" @click="$emit('edit', orden)">Editar</BaseButton>
      <BaseButton size="sm" icon="payments" @click="$emit('pagar', orden)">Registrar pago</BaseButton>
      <BaseButton variant="ghost" size="sm" icon="refresh" @click="abrirCambioEstado">Cambiar estado</BaseButton>
      <BaseButton variant="ghost" size="sm" icon="eye" @click="$emit('detalles', orden)">Ver detalles</BaseButton>
      <BaseButton variant="ghost" size="sm" icon="trash" class="col-span-2 text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-500/10" @click="$emit('eliminar', orden)">Eliminar</BaseButton>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed, ref } from 'vue'
import BaseButton from './BaseButton.vue'
import BaseCard from './BaseCard.vue'
import BaseInput from './BaseInput.vue'
import StatusBadge from './StatusBadge.vue'
import { resolveEstado } from '../constants/estados'
import { useFormatters } from '../composables/useFormatters'

const props = defineProps({
  orden: { type: Object, required: true },
  clienteNombre: { type: String, default: 'Cliente' },
  estados: { type: Array, required: true },
  index: { type: Number, default: 0 },
})

const emit = defineEmits(['edit', 'pagar', 'detalles', 'cambiar-estado', 'eliminar'])

const { formatCurrency, formatDate } = useFormatters()

const cambiandoEstado = ref(false)
const nuevoEstado = ref(props.orden.estado || props.estados[0])

function abrirCambioEstado() {
  nuevoEstado.value = props.orden.estado || props.estados[0]
  cambiandoEstado.value = true
}

function confirmarEstado() {
  emit('cambiar-estado', { orden: props.orden, estado: nuevoEstado.value })
  cambiandoEstado.value = false
}

// Mismo color que StatusBadge.vue y el donut del dashboard (vienen del
// mismo resolveEstado), para que el acento de la tarjeta, el badge y
// los charts sean consistentes.
const accentColor = computed(() => resolveEstado(props.orden.estado).color)

// Acento izquierdo por estado + retardo escalonado de entrada (el grid
// de OrdenesView pasa `index` para que las tarjetas aparezcan en cascada).
const cardStyle = computed(() => ({
  borderLeftColor: accentColor.value,
  borderLeftWidth: '3px',
  animationDelay: `${Math.min(props.index, 12) * 45}ms`,
}))

const estadoKey = computed(() => resolveEstado(props.orden.estado).key)
const esFinal = computed(() => ['entregado', 'entregado_sr', 'cancelado'].includes(estadoKey.value))

// Si la orden ya tiene fecha de entrega, "dias en taller" es la duracion
// real de la reparacion (fecha_entrega - fecha_ingreso), no crece para
// siempre. Sin fecha de entrega: si sigue activa, cuenta hasta hoy; si ya
// esta entregada/cancelada pero sin fecha registrada (datos historicos
// importados), no hay forma honesta de saber cuanto duro, asi que se
// muestra "-" en vez de inventar un numero.
const diasEnTaller = computed(() => {
  if (!props.orden.fecha_ingreso) return null
  if (props.orden.fecha_entrega) {
    const ms = new Date(props.orden.fecha_entrega).getTime() - new Date(props.orden.fecha_ingreso).getTime()
    return Math.max(Math.floor(ms / 86_400_000), 0)
  }
  if (esFinal.value) return null
  const ms = Date.now() - new Date(props.orden.fecha_ingreso).getTime()
  return Math.max(Math.floor(ms / 86_400_000), 0)
})

// La prioridad no existe como campo en la base de datos: se calcula
// segun cuantos dias lleva la orden sin entregarse. Ordenes ya
// entregadas o canceladas no la necesitan.
const prioridad = computed(() => {
  if (esFinal.value) return null

  if (diasEnTaller.value > 7) return { label: 'Urgente', tone: 'red' }
  if (diasEnTaller.value > 3) return { label: 'Atencion', tone: 'orange' }
  return { label: 'Normal', tone: 'slate' }
})

const prioridadClasses = computed(() => ({
  red: 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300',
  orange: 'bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300',
  slate: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
}[prioridad.value?.tone]))

// Progreso de cobro (visual, no toca el dato de saldo del backend).
const abonado = computed(() => Math.max(Number(props.orden.valor || 0) - Number(props.orden.saldo || 0), 0))
const pctPago = computed(() => {
  const valor = Number(props.orden.valor || 0)
  if (valor <= 0) return 0
  return Math.min(Math.max((abonado.value / valor) * 100, 0), 100)
})
const esPagado = computed(() => Number(props.orden.saldo || 0) <= 0)
const pctLabel = computed(() => `${Math.round(pctPago.value)}%`)
</script>
