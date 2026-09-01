<template>
  <div class="space-y-6">
    <PageHeader title="Inventario" subtitle="Gestión de productos, stock, proveedores y movimiento de mercancía.">
      <template #actions>
        <BaseButton icon="plus" @click="openCreate">Nuevo producto</BaseButton>
      </template>
    </PageHeader>

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

    <!-- Categorías -->
    <section v-if="activeTab === 'categorias'">
      <BaseCard content-class="p-4">
        <BaseTable :columns="[{ key: 'nombre', label: 'Nombre' }]" :rows="categorias" :loading="loading" />
      </BaseCard>
    </section>

    <!-- Proveedores -->
    <section v-if="activeTab === 'proveedores'">
      <BaseCard content-class="p-4">
        <BaseTable :columns="[{ key: 'nombre', label: 'Nombre' }, { key: 'telefono', label: 'Teléfono' }, { key: 'email', label: 'Email' }]" :rows="proveedores" :loading="loading" />
      </BaseCard>
    </section>

    <!-- Modal Producto -->
    <BaseModal v-model="modalOpen" title="Nuevo producto" subtitle="Registro de producto en inventario.">
      <form class="grid gap-4" @submit.prevent="saveProducto">
        <BaseInput v-model="form.nombre" label="Nombre" required />
        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.codigo_sku" label="SKU" />
          <ComboSelect v-model="form.categoria_id" label="Categoría" :options="categoriaOptions" required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.precio_compra" label="Precio Compra" type="number" />
          <BaseInput v-model="form.precio_venta" label="Precio Venta" type="number" required />
        </div>
        <BaseInput v-model="form.stock_minimo" label="Stock Mínimo" type="number" />
        <BaseButton type="submit" :loading="saving">Guardar</BaseButton>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseTable from '../components/BaseTable.vue'
import PageHeader from '../components/PageHeader.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseInput from '../components/BaseInput.vue'
import ComboSelect from '../components/ComboSelect.vue'
import { inventarioApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

const { formatCurrency } = useFormatters()
const { loading, run } = useApiState()
const saving = ref(false)

const tabs = [
  { key: 'productos', label: 'Productos' },
  { key: 'movimientos', label: 'Movimientos (Kardex)' },
  { key: 'categorias', label: 'Categorías' },
  { key: 'proveedores', label: 'Proveedores' },
]
const activeTab = ref('productos')
const productos = ref([])
const movimientos = ref([])
const categorias = ref([])
const proveedores = ref([])
const modalOpen = ref(false)

const form = reactive({ nombre: '', codigo_sku: '', precio_compra: 0, precio_venta: 0, stock_minimo: 0, categoria_id: '' })

const categoriaOptions = computed(() =>
  categorias.value.map(c => ({ value: c.id, label: c.nombre }))
)

const productoColumns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'codigo_sku', label: 'SKU' },
  { key: 'stock_actual', label: 'Stock' },
  { key: 'precio_venta', label: 'Precio Venta' },
  { key: 'actions', label: '' },
]

const movimientoColumns = [
  { key: 'producto_id', label: 'Producto' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'cantidad', label: 'Cantidad' },
  { key: 'created_at', label: 'Fecha' },
]

async function loadData() {
  const [prodRes, movRes, catRes, provRes] = await Promise.all([
    run(() => inventarioApi.listProductos()),
    run(() => inventarioApi.listMovimientos()),
    run(() => inventarioApi.listCategorias()),
    run(() => inventarioApi.listProveedores())
  ])
  productos.value = prodRes.data
  movimientos.value = movRes.data
  categorias.value = catRes.data
  proveedores.value = provRes.data
}

function openCreate() {
  form.nombre = ''
  form.codigo_sku = ''
  form.precio_compra = 0
  form.precio_venta = 0
  form.stock_minimo = 0
  form.categoria_id = ''
  modalOpen.value = true
}

async function saveProducto() {
  saving.value = true
  try {
    await run(() => inventarioApi.createProducto(form))
    modalOpen.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

function openEdit(prod) {
    // Implementar edición en el futuro
}

onMounted(loadData)
</script>
