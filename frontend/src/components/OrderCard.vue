<template>
  <BaseCard content-class="p-4" class="flex flex-col transition hover:-translate-y-0.5 hover:shadow-lift">
    <div class="flex items-start justify-between gap-2">
      <StatusBadge :value="orden.estado || 'recibido'" />
      <span v-if="prioridad" :class="prioridadClasses" class="rounded-full px-2.5 py-1 text-xs font-semibold">{{ prioridad.label }}</span>
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
        <p class="mt-0.5 font-medium text-slate-700 dark:text-slate-200">{{ diasEnTaller }} dias</p>
      </div>
      <div>
        <p class="text-slate-400">Saldo</p>
        <p class="mt-0.5 font-semibold text-slate-950 dark:text-white">{{ formatCurrency(orden.saldo) }}</p>
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
      <BaseButton variant="secondary" size="sm" icon="payments" @click="$emit('pagar', orden)">Registrar pago</BaseButton>
      <BaseButton variant="ghost" size="sm" icon="refresh" @click="abrirCambioEstado">Cambiar estado</BaseButton>
      <BaseButton variant="ghost" size="sm" icon="eye" @click="$emit('detalles', orden)">Ver detalles</BaseButton>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed, ref } from 'vue'
import BaseButton from './BaseButton.vue'
import BaseCard from './BaseCard.vue'
import BaseInput from './BaseInput.vue'
import StatusBadge from './StatusBadge.vue'
import { useFormatters } from '../composables/useFormatters'

const props = defineProps({
  orden: { type: Object, required: true },
  clienteNombre: { type: String, default: 'Cliente' },
  estados: { type: Array, required: true },
})

const emit = defineEmits(['edit', 'pagar', 'detalles', 'cambiar-estado'])

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

const diasEnTaller = computed(() => {
  if (!props.orden.fecha_ingreso) return 0
  const ms = Date.now() - new Date(props.orden.fecha_ingreso).getTime()
  return Math.max(Math.floor(ms / 86_400_000), 0)
})

// La prioridad no existe como campo en la base de datos: se calcula
// segun cuantos dias lleva la orden sin entregarse. Ordenes ya
// entregadas o canceladas no la necesitan.
const prioridad = computed(() => {
  const estado = (props.orden.estado || '').toLowerCase()
  if (estado.includes('entreg') || estado.includes('cancel')) return null

  if (diasEnTaller.value > 7) return { label: 'Urgente', tone: 'red' }
  if (diasEnTaller.value > 3) return { label: 'Atencion', tone: 'orange' }
  return { label: 'Normal', tone: 'slate' }
})

const prioridadClasses = computed(() => ({
  red: 'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300',
  orange: 'bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300',
  slate: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
}[prioridad.value?.tone]))
</script>
