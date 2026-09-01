<template>
  <div class="space-y-6">
    <PageHeader title="Inventario" subtitle="Gestión de productos, stock, compras y movimiento de mercancía.">
      <template #actions>
        <div class="flex items-center gap-2">
          <BaseButton variant="secondary" icon="plus" @click="openCompra">Registrar compra</BaseButton>
          <BaseButton icon="plus" @click="openCreate">Nuevo producto</BaseButton>
        </div>
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
          <template #tipo="{ value }">
            <span
              class="rounded-full px-2.5 py-1 text-xs font-semibold capitalize"
              :class="{
                'bg-green-100 text-green-700 dark:bg-green-500/15 dark:text-green-300': value === 'entrada',
                'bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300': value === 'salida',
                'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300': value === 'ajuste' || value === 'merma',
              }"
            >{{ value }}</span>
          </template>
          <template #motivo="{ value }">
            {{ value || '-' }}
          </template>
          <template #created_at="{ value }">
            {{ formatDate(value) }}
          </template>
        </BaseTable>
      </BaseCard>
    </section>

    <!-- Modal Producto -->
    <BaseModal v-model="modalOpen" title="Nuevo producto" subtitle="Registro de producto en inventario.">
      <form class="grid gap-4" @submit.prevent="saveProducto">
        <BaseInput v-model="form.nombre" label="Nombre" required />
        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.codigo_sku" label="SKU" :placeholder="form.id ? '' : 'Automático'" />
          <ComboSelect v-model="form.categoria_id" label="Categoría" :options="categoriaOptions" required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.precio_compra" label="Precio Compra" type="number" />
          <BaseInput v-model="form.precio_venta" label="Precio Venta" type="number" required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.stock_actual" label="Stock inicial" type="number" />
          <BaseInput v-model="form.stock_minimo" label="Stock mínimo" type="number" />
        </div>
        <BaseButton type="submit" :loading="saving">Guardar</BaseButton>
      </form>
    </BaseModal>

    <!-- Modal Compra -->
    <BaseModal v-model="compraModalOpen" title="Registrar compra" subtitle="Compra de producto: suma stock, registra en Kardex y genera egreso en caja.">
      <form class="grid gap-4" @submit.prevent="saveCompra">
        <ComboSelect v-model="compraForm.producto_id" label="Producto" :options="productosOptions" required />
        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="compraForm.cantidad" label="Cantidad" type="number" required min="1" />
          <BaseInput v-model="compraForm.valor_unitario" label="Costo unitario" type="number" required />
        </div>
        <div class="rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60">
          <p class="text-sm text-slate-600 dark:text-slate-300">
            Total egreso: <strong class="text-slate-950 dark:text-white">{{ formatCurrency(compraTotal) }}</strong>
          </p>
        </div>
        <BaseInput v-model="compraForm.metodo_pago" label="Método de pago" type="select">
          <option value="Efectivo">Efectivo</option>
          <option value="Transferencia">Transferencia</option>
          <option value="Nequi">Nequi</option>
          <option value="Daviplata">Daviplata</option>
          <option value="Tarjeta">Tarjeta</option>
          <option value="Otro">Otro</option>
        </BaseInput>
        <BaseInput v-model="compraForm.descripcion" label="Descripción" placeholder="Ej. Compra a proveedor X" textarea />
        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" @click="compraModalOpen = false">Cancelar</BaseButton>
          <BaseButton type="submit" :loading="savingCompra">Registrar compra</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
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

const { formatCurrency, formatDate } = useFormatters()
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

// --- Producto ---
const form = reactive({ nombre: '', codigo_sku: '', precio_compra: 0, precio_venta: 0, stock_actual: 0, stock_minimo: 0, categoria_id: '' })

const categoriaOptions = computed(() =>
  categorias.value.map(c => ({ value: c.id, label: c.nombre }))
)

const productosOptions = computed(() =>
  productos.value.map(p => ({
    value: p.id,
    label: `${p.nombre}${p.codigo_sku ? ` (${p.codigo_sku})` : ''} — Stock: ${p.stock_actual}`,
  }))
)

const productoColumns = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'codigo_sku', label: 'SKU' },
  { key: 'stock_actual', label: 'Stock' },
  { key: 'stock_minimo', label: 'Mínimo' },
  { key: 'precio_venta', label: 'Precio Venta' },
]

const movimientoColumns = [
  { key: 'producto_id', label: 'Producto' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'cantidad', label: 'Cantidad' },
  { key: 'motivo', label: 'Motivo' },
  { key: 'created_at', label: 'Fecha' },
]

// --- Compra ---
const compraModalOpen = ref(false)
const savingCompra = ref(false)
const compraForm = reactive({ producto_id: '', cantidad: 1, valor_unitario: 0, metodo_pago: 'Efectivo', descripcion: '' })

const compraTotal = computed(() => Number(compraForm.cantidad || 0) * Number(compraForm.valor_unitario || 0))

// Auto-llenar costo unitario con precio_compra del producto
watch(() => compraForm.producto_id, (nuevoId) => {
  const prod = productos.value.find(p => Number(p.id) === Number(nuevoId))
  if (prod) compraForm.valor_unitario = prod.precio_compra || 0
})

async function loadData() {
  loading.value = true
  try {
    const [prodRes, movRes, catRes] = await Promise.allSettled([
      inventarioApi.listProductos(),
      inventarioApi.listMovimientos(),
      inventarioApi.listCategorias(),
    ])
    if (prodRes.status === 'fulfilled') {
      productos.value = prodRes.value.data
    } else {
      console.error('Error al cargar productos:', prodRes.reason)
      ui.toast('No se pudieron cargar los productos', 'error')
    }
    if (movRes.status === 'fulfilled') {
      movimientos.value = movRes.value.data
    } else {
      console.error('Error al cargar movimientos (Kardex):', movRes.reason)
      ui.toast('No se pudieron cargar los movimientos', 'error')
    }
    if (catRes.status === 'fulfilled') categorias.value = catRes.value.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  delete form.id
  form.nombre = ''
  form.codigo_sku = ''
  form.precio_compra = 0
  form.precio_venta = 0
  form.stock_actual = 0
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
  form.stock_actual = prod.stock_actual
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

function openCompra() {
  compraForm.producto_id = ''
  compraForm.cantidad = 1
  compraForm.valor_unitario = 0
  compraForm.metodo_pago = 'Efectivo'
  compraForm.descripcion = ''
  compraModalOpen.value = true
}

async function saveCompra() {
  savingCompra.value = true
  try {
    await run(() => inventarioApi.registrarCompra({
      producto_id: Number(compraForm.producto_id),
      cantidad: Number(compraForm.cantidad),
      valor_unitario: Number(compraForm.valor_unitario),
      metodo_pago: compraForm.metodo_pago,
      descripcion: compraForm.descripcion,
    }), 'Compra registrada — stock, Kardex y egreso actualizados')
    compraModalOpen.value = false
    await loadData()
  } finally {
    savingCompra.value = false
  }
}

onMounted(loadData)
</script>
