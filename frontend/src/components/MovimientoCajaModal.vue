<template>
  <BaseModal v-model="isOpen" :title="copy.title" :subtitle="copy.subtitle">
    <form class="grid gap-4" @submit.prevent="submit">
      <div class="grid gap-4 sm:grid-cols-2">
        <BaseInput v-model="form.categoria" label="Categoria" type="select" required>
          <option v-for="categoria in categorias" :key="categoria" :value="categoria">{{ categoria }}</option>
        </BaseInput>
        <BaseInput v-model="form.valor" label="Valor" type="number" required />
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <BaseInput v-model="form.metodo_pago" label="Metodo de pago" type="select" required>
          <option value="efectivo">Efectivo</option>
          <option value="transferencia">Transferencia</option>
          <option value="nequi">Nequi</option>
          <option value="daviplata">Daviplata</option>
          <option value="tarjeta">Tarjeta</option>
          <option value="otro">Otro</option>
        </BaseInput>
      </div>

      <BaseInput v-model="form.descripcion" :label="copy.descripcionLabel" :placeholder="copy.descripcionPlaceholder" textarea required />

      <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-900">
        <div class="flex items-center justify-between gap-4">
          <div>
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Vista previa</p>
            <p class="mt-1 text-lg font-semibold text-slate-950 dark:text-white">{{ formattedValue }}</p>
          </div>
          <FinanceTypeBadge :value="tipo" />
        </div>
      </div>

      <div class="flex justify-end gap-2">
        <BaseButton variant="secondary" @click="isOpen = false">Cancelar</BaseButton>
        <BaseButton type="submit" :loading="loading">Guardar movimiento</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import BaseButton from './BaseButton.vue'
import BaseInput from './BaseInput.vue'
import BaseModal from './BaseModal.vue'
import FinanceTypeBadge from './FinanceTypeBadge.vue'
import { useFormatters } from '../composables/useFormatters'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  tipo: { type: String, default: 'egreso' }, // 'egreso' | 'ingreso'
})

const emit = defineEmits(['update:modelValue', 'save'])
const { formatCurrency } = useFormatters()

const categoriasPorTipo = {
  egreso: ['arriendo', 'empleado', 'servicios', 'herramientas', 'transporte', 'compra', 'prestamo', 'otros'],
  // Ingresos que no vienen de una orden facturada: ventas de mostrador,
  // pilas, accesorios, servicios rapidos sin ficha de cliente.
  ingreso: ['venta', 'accesorio', 'pila', 'servicio_rapido', 'otros'],
}

const copyPorTipo = {
  egreso: {
    title: 'Nuevo egreso',
    subtitle: 'Registra gastos operativos, compras, arriendos, servicios o pagos internos.',
    descripcionLabel: 'Descripcion',
    descripcionPlaceholder: 'Ej. Pago arriendo mayo',
  },
  ingreso: {
    title: 'Nuevo ingreso',
    subtitle: 'Ventas u otros ingresos que no requieren factura ni datos del cliente.',
    descripcionLabel: 'Descripcion',
    descripcionPlaceholder: 'Ej. Venta de pila para iPhone 11',
  },
}

const categorias = computed(() => categoriasPorTipo[props.tipo] || categoriasPorTipo.egreso)
const copy = computed(() => copyPorTipo[props.tipo] || copyPorTipo.egreso)

const form = reactive({
  categoria: 'otros',
  valor: '',
  metodo_pago: 'efectivo',
  descripcion: '',
})

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const formattedValue = computed(() => formatCurrency(form.valor || 0))

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      Object.assign(form, {
        categoria: 'otros',
        valor: '',
        metodo_pago: 'efectivo',
        descripcion: '',
      })
    }
  },
)

function submit() {
  emit('save', {
    tipo: props.tipo,
    categoria: form.categoria,
    valor: Number(form.valor || 0),
    metodo_pago: form.metodo_pago,
    descripcion: form.descripcion,
  })
}
</script>
