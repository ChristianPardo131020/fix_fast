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

    <!-- Productos -->
    <section v-if="activeTab === 'productos'">
      <BaseCard content-class="p-4">
        <BaseTable :columns="productoColumns" :rows="productos" :loading="loading">
          <template #precio_venta="{ row }">{{ formatCurrency(row.precio_venta) }}</template>
          <template #actions="{ row }">
             <BaseButton variant="ghost" size="sm" @click="openEdit(row)">Editar</BaseButton>
          </template>
        </BaseTable>
      </BaseCard>
    </section>

    <!-- Movimientos -->
    <section v-if="activeTab === 'movimientos'">
      <BaseCard content-class="p-4">
        <BaseTable :columns="movimientoColumns" :rows="movimientos" :loading="loading" />
      </BaseCard>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import BaseTable from '../components/BaseTable.vue'
import PageHeader from '../components/PageHeader.vue'
import { inventarioApi } from '../api/resources'
import { useApiState } from '../composables/useApiState'
import { useFormatters } from '../composables/useFormatters'

const { formatCurrency } = useFormatters()
const { loading, run } = useApiState()

const tabs = [
  { key: 'productos', label: 'Productos' },
  { key: 'movimientos', label: 'Movimientos (Kardex)' },
  { key: 'categorias', label: 'Categorías' },
  { key: 'proveedores', label: 'Proveedores' },
]
const activeTab = ref('productos')
const productos = ref([])
const movimientos = ref([])

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
  const [prodRes, movRes] = await Promise.all([
    run(() => inventarioApi.listProductos()),
    run(() => inventarioApi.listMovimientos())
  ])
  productos.value = prodRes.data
  movimientos.value = movRes.data
}

function openCreate() {}
function openEdit(prod) {}

onMounted(loadData)
</script>
