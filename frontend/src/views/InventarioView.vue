<template>
  <div class="space-y-6">
    <PageHeader title="Inventario" subtitle="Gestión de productos, stock y movimiento de mercancía.">
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

    <!-- Productos -->
    <section v-if="activeTab === 'productos'">
      <BaseCard content-class="p-4">
        <BaseTable :columns="productoColumns" :rows="productos" :loading="loading">
          <template #actions="{ row }">
            <div class="flex justify-end gap-2">
              <BaseButton variant="secondary" size="sm" icon="edit" @click="openEdit(row)">Editar</BaseButton>
              <BaseButton variant="danger" size="sm" icon="trash" @click="removeProducto(row)">Eliminar</BaseButton>
            </div>
          </template>
          <template #precio_venta="{ value }">
            {{ formatCurrency(value) }}
          </template>
          <template #stock_actual="{ value }">
            <span :class="value > 0 ? 'text-green-600' : 'text-red-500'">{{ value }}</span>
          </template>
        </BaseTable>
      </BaseCard>
    </section>

    <!-- Movimientos (Kardex) -->
    <section v-if="activeTab === 'movimientos'">
      <BaseCard content-class="p-4">
        <BaseTable :columns="movimientoColumns" :rows="movimientos" :loading="loading">
          <template #producto_id="{ row }">
            {{ row.producto ? row.producto.nombre : 'ID: ' + row.producto_id }}
          </template>
          <template #created_at="{ value }">
            {{ new Date(value).toLocaleDateString() }}
          </template>
        </BaseTable>
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
import { useUiStore } from '../stores/ui'

const { formatCurrency } = useFormatters()
const { loading, run } = useApiState()
const saving = ref(false)
const ui = useUiStore()

const tabs = [
  { key: 'productos', label: 'Productos' },
  { key: 'movimientos', label: 'Movimientos (Kardex)' },
]
const activeTab = ref('productos')
const productos = ref([])
const movimientos = ref([])
const categorias = ref([])
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
]

const movimientoColumns = [
  { key: 'producto_id', label: 'Producto' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'cantidad', label: 'Cantidad' },
  { key: 'created_at', label: 'Fecha' },
]

async function loadData() {
  const [prodRes, movRes, catRes] = await Promise.all([
    run(() => inventarioApi.listProductos()),
    run(() => inventarioApi.listMovimientos()),
    run(() => inventarioApi.listCategorias()),
  ])
  productos.value = prodRes.data
  movimientos.value = movRes.data
  categorias.value = catRes.data
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
    if (form.id) {
      await run(() => inventarioApi.updateProducto(form.id, form))
    } else {
      await run(() => inventarioApi.createProducto(form))
    }
    modalOpen.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

function openEdit(prod) {
  form.id = prod.id
  form.nombre = prod.nombre
  form.codigo_sku = prod.codigo_sku
  form.precio_compra = prod.precio_compra
  form.precio_venta = prod.precio_venta
  form.stock_minimo = prod.stock_minimo
  form.categoria_id = prod.categoria_id
  modalOpen.value = true
}

async function removeProducto(prod) {
  const confirmed = await ui.confirm({
    title: `Eliminar producto "${prod.nombre}"`,
    message: 'Se eliminará el producto y sus movimientos de inventario.'
  })
  if (!confirmed) return

  await run(() => inventarioApi.removeProducto(prod.id), 'Producto eliminado')
  await loadData()
}

onMounted(loadData)
</script>
