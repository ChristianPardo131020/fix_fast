<template>
  <div class="relative" ref="containerRef">
    <!-- Trigger Button -->
    <button
      type="button"
      class="inline-flex items-center gap-2 rounded-xl border px-3 py-2 text-sm font-medium transition-all duration-200"
      :class="hasSelection
        ? 'border-brand-300 bg-brand-50 text-brand-700 shadow-sm shadow-brand-100/50 hover:bg-brand-100 dark:border-brand-500/30 dark:bg-brand-500/10 dark:text-brand-300 dark:shadow-none dark:hover:bg-brand-500/15'
        : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800'"
      @click="toggleOpen"
    >
      <AppIcon name="calendar" class="!h-4 !w-4 shrink-0" />
      <span class="max-w-[14rem] truncate">{{ displayLabel }}</span>
      <AppIcon name="chevron-down" class="!h-3.5 !w-3.5 shrink-0 transition-transform" :class="{ 'rotate-180': open }" />
    </button>

    <!-- Dropdown Calendar -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="scale-95 opacity-0"
        enter-to-class="scale-100 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="scale-100 opacity-100"
        leave-to-class="scale-95 opacity-0"
      >
        <div
          v-if="open"
          ref="dropdownRef"
          class="fixed z-[9999] w-[340px] rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-900/10 dark:border-slate-700 dark:bg-slate-900 dark:shadow-black/30"
          :style="dropdownStyle"
        >
          <!-- Presets Strip -->
          <div class="flex flex-wrap gap-1.5 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
            <button
              v-for="preset in presets"
              :key="preset.key"
              type="button"
              class="rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide transition-all"
              :class="isPresetActive(preset)
                ? 'border-brand-400 bg-brand-500 text-white shadow-sm dark:border-brand-500 dark:bg-brand-600'
                : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-slate-50 hover:text-slate-700 dark:border-slate-700 dark:text-slate-400 dark:hover:border-slate-600 dark:hover:bg-slate-800'"
              @click="applyPreset(preset)"
            >
              {{ preset.label }}
            </button>
          </div>

          <!-- Month/Year Navigation -->
          <div class="flex items-center justify-between px-4 py-3">
            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200"
              @click="navigateMonth(-1)"
            >
              <AppIcon name="chevron-left" class="!h-4 !w-4" />
            </button>

            <div class="flex items-center gap-1">
              <button
                type="button"
                class="rounded-lg px-2 py-1 text-sm font-bold text-slate-700 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800"
                @click="selectEntireMonth"
              >
                {{ monthNames[viewMonth] }}
              </button>
              <button
                type="button"
                class="rounded-lg px-2 py-1 text-sm font-bold text-slate-700 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800"
                @click="selectEntireYear"
              >
                {{ viewYear }}
              </button>
            </div>

            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200"
              @click="navigateMonth(1)"
            >
              <AppIcon name="chevron-right" class="!h-4 !w-4" />
            </button>
          </div>

          <!-- Day Labels -->
          <div class="grid grid-cols-7 px-4">
            <div v-for="dayName in dayLabels" :key="dayName" class="py-1 text-center text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              {{ dayName }}
            </div>
          </div>

          <!-- Calendar Grid -->
          <div class="grid grid-cols-7 gap-y-0.5 px-4 pb-4">
            <div v-for="(cell, i) in calendarCells" :key="i">
              <button
                v-if="cell.day"
                type="button"
                class="relative flex h-9 w-full items-center justify-center rounded-lg text-sm font-medium transition-all duration-150"
                :class="dayClass(cell)"
                @click="onDayClick(cell, $event)"
              >
                <span class="relative z-10">{{ cell.day }}</span>
                <span v-if="isToday(cell)" class="absolute bottom-1 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full" :class="isInRange(cell) ? 'bg-white/80' : 'bg-brand-500'" />
              </button>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-between border-t border-slate-100 px-4 py-3 dark:border-slate-800">
            <span class="text-xs text-slate-400 dark:text-slate-500">
              {{ footerHint }}
            </span>
            <div class="flex gap-2">
              <button
                v-if="hasSelection"
                type="button"
                class="rounded-lg px-3 py-1.5 text-xs font-medium text-slate-500 transition hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800"
                @click="clearSelection"
              >
                Limpiar
              </button>
              <button
                type="button"
                class="rounded-lg bg-brand-500 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:bg-brand-600 dark:bg-brand-600 dark:hover:bg-brand-500"
                @click="open = false"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import AppIcon from './AppIcon.vue'
import { toISO } from '../utils/dateRanges'

const props = defineProps({
  // { desde: 'YYYY-MM-DD' | '', hasta: 'YYYY-MM-DD' | '' }
  modelValue: { type: Object, required: true },
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const containerRef = ref(null)
const dropdownRef = ref(null)
const dropdownStyle = ref({})

const now = new Date()
const todayISO = toISO(now)

// Calendar navigation state
const viewMonth = ref(now.getMonth())  // 0-11
const viewYear = ref(now.getFullYear())

const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const dayLabels = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do']

// Presets
const presets = [
  { key: 'hoy', label: 'Hoy', range: () => { const t = toISO(new Date()); return { desde: t, hasta: t } } },
  { key: 'semana', label: 'Semana', range: () => {
    const d = new Date()
    const day = d.getDay()
    const diff = (day === 0 ? -6 : 1) - day
    const start = new Date(d)
    start.setDate(d.getDate() + diff)
    const end = new Date(start)
    end.setDate(start.getDate() + 6)
    return { desde: toISO(start), hasta: toISO(end) }
  }},
  { key: 'mes', label: 'Este mes', range: () => {
    const d = new Date()
    return { desde: toISO(new Date(d.getFullYear(), d.getMonth(), 1)), hasta: toISO(new Date(d.getFullYear(), d.getMonth() + 1, 0)) }
  }},
  { key: 'anio', label: 'Este año', range: () => {
    const y = new Date().getFullYear()
    return { desde: toISO(new Date(y, 0, 1)), hasta: toISO(new Date(y, 11, 31)) }
  }},
  { key: 'todo', label: 'Todo', range: () => ({ desde: '', hasta: '' }) },
]

// -- Selection logic (range-based: desde/hasta) --

const hasSelection = computed(() => !!(props.modelValue.desde || props.modelValue.hasta))

function isPresetActive(preset) {
  const r = preset.range()
  return r.desde === (props.modelValue.desde || '') && r.hasta === (props.modelValue.hasta || '')
}

function applyPreset(preset) {
  const r = preset.range()
  emit('update:modelValue', { ...r })
  if (r.desde) {
    const d = parseISO(r.desde)
    viewMonth.value = d.getMonth()
    viewYear.value = d.getFullYear()
  }
}

function parseISO(str) {
  const [y, m, d] = str.split('-').map(Number)
  return new Date(y, m - 1, d)
}

// Calendar cell generation
const calendarCells = computed(() => {
  const firstDay = new Date(viewYear.value, viewMonth.value, 1)
  let startDow = firstDay.getDay() // 0=Sun ... 6=Sat
  // Adjust for Monday start: Mon=0, Tue=1, ... Sun=6
  startDow = startDow === 0 ? 6 : startDow - 1

  const daysInMonth = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()

  const cells = []
  // Empty cells before the first day
  for (let i = 0; i < startDow; i++) {
    cells.push({ day: null })
  }
  // Day cells
  for (let d = 1; d <= daysInMonth; d++) {
    const iso = `${viewYear.value}-${String(viewMonth.value + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    cells.push({ day: d, iso, month: viewMonth.value, year: viewYear.value })
  }
  return cells
})

function isToday(cell) {
  return cell.iso === todayISO
}

function isInRange(cell) {
  if (!cell.iso) return false
  const desde = props.modelValue.desde || ''
  const hasta = props.modelValue.hasta || ''
  if (!desde && !hasta) return false
  if (desde && !hasta) return cell.iso === desde
  if (!desde && hasta) return cell.iso === hasta
  return cell.iso >= desde && cell.iso <= hasta
}

function isRangeStart(cell) {
  return cell.iso && cell.iso === props.modelValue.desde
}

function isRangeEnd(cell) {
  return cell.iso && cell.iso === props.modelValue.hasta
}

function isSingleDay(cell) {
  return cell.iso && props.modelValue.desde === props.modelValue.hasta && cell.iso === props.modelValue.desde
}

function dayClass(cell) {
  if (!cell.iso) return ''
  const inRange = isInRange(cell)
  const isStart = isRangeStart(cell)
  const isEnd = isRangeEnd(cell)
  const single = isSingleDay(cell)
  const today = isToday(cell)

  if (single) {
    return 'bg-brand-500 text-white shadow-sm shadow-brand-300/40 dark:bg-brand-600 dark:shadow-brand-800/40'
  }
  if (isStart || isEnd) {
    return 'bg-brand-500 text-white shadow-sm shadow-brand-300/40 dark:bg-brand-600 dark:shadow-brand-800/40'
  }
  if (inRange) {
    return 'bg-brand-100 text-brand-700 dark:bg-brand-500/20 dark:text-brand-300'
  }
  if (today) {
    return 'text-brand-600 font-bold dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-500/10'
  }
  return 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
}

function onDayClick(cell, event) {
  if (!cell.iso) return

  const desde = props.modelValue.desde
  const hasta = props.modelValue.hasta

  if (event.shiftKey && desde) {
    // Shift+click extends the range from the existing start
    const newRange = desde <= cell.iso
      ? { desde, hasta: cell.iso }
      : { desde: cell.iso, hasta: desde }
    emit('update:modelValue', newRange)
    return
  }

  // If there's already a start date selected (but no end yet or same day), set end
  if (desde && desde === hasta && cell.iso !== desde) {
    const newRange = desde <= cell.iso
      ? { desde, hasta: cell.iso }
      : { desde: cell.iso, hasta: desde }
    emit('update:modelValue', newRange)
    return
  }

  // Single click: select just this day
  emit('update:modelValue', { desde: cell.iso, hasta: cell.iso })
}

function selectEntireMonth() {
  const start = `${viewYear.value}-${String(viewMonth.value + 1).padStart(2, '0')}-01`
  const lastDay = new Date(viewYear.value, viewMonth.value + 1, 0).getDate()
  const end = `${viewYear.value}-${String(viewMonth.value + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
  emit('update:modelValue', { desde: start, hasta: end })
}

function selectEntireYear() {
  const start = `${viewYear.value}-01-01`
  const end = `${viewYear.value}-12-31`
  emit('update:modelValue', { desde: start, hasta: end })
}

function clearSelection() {
  emit('update:modelValue', { desde: '', hasta: '' })
}

function navigateMonth(dir) {
  let m = viewMonth.value + dir
  let y = viewYear.value
  if (m < 0) { m = 11; y-- }
  if (m > 11) { m = 0; y++ }
  viewMonth.value = m
  viewYear.value = y
}

// -- Display label --
const displayLabel = computed(() => {
  const desde = props.modelValue.desde
  const hasta = props.modelValue.hasta

  if (!desde && !hasta) return 'Todo el periodo'

  if (desde === hasta) {
    // Single day
    if (desde === todayISO) return 'Hoy'
    return formatDateShort(desde)
  }

  // Check if it's an entire month
  if (desde && hasta) {
    const dStart = parseISO(desde)
    const dEnd = parseISO(hasta)
    if (dStart.getDate() === 1) {
      const lastOfMonth = new Date(dStart.getFullYear(), dStart.getMonth() + 1, 0).getDate()
      if (dEnd.getDate() === lastOfMonth && dStart.getMonth() === dEnd.getMonth() && dStart.getFullYear() === dEnd.getFullYear()) {
        return `${monthNames[dStart.getMonth()]} ${dStart.getFullYear()}`
      }
    }
    // Check if entire year
    if (dStart.getMonth() === 0 && dStart.getDate() === 1 && dEnd.getMonth() === 11 && dEnd.getDate() === 31 && dStart.getFullYear() === dEnd.getFullYear()) {
      return `Año ${dStart.getFullYear()}`
    }
  }

  return `${formatDateShort(desde)} — ${formatDateShort(hasta)}`
})

function formatDateShort(iso) {
  if (!iso) return ''
  const d = parseISO(iso)
  return `${d.getDate()} ${monthNames[d.getMonth()].substring(0, 3)} ${d.getFullYear()}`
}

const footerHint = computed(() => {
  if (!hasSelection.value) return 'Click para seleccionar un día'
  const desde = props.modelValue.desde
  const hasta = props.modelValue.hasta
  if (desde === hasta) return 'Click otro día para rango, Shift+click para extender'
  return 'Click un día para nueva selección'
})

// -- Position dropdown --
function positionDropdown() {
  if (!containerRef.value || !dropdownRef.value) return
  const trigger = containerRef.value.getBoundingClientRect()
  const dropH = dropdownRef.value.offsetHeight
  const dropW = 340
  const viewH = window.innerHeight
  const viewW = window.innerWidth

  let top = trigger.bottom + 8
  let left = trigger.left

  // If dropdown goes below viewport, show above
  if (top + dropH > viewH - 16) {
    top = trigger.top - dropH - 8
  }
  // If dropdown goes off right edge, align right
  if (left + dropW > viewW - 16) {
    left = viewW - dropW - 16
  }
  // Don't go off left edge
  if (left < 16) left = 16

  dropdownStyle.value = { top: `${top}px`, left: `${left}px` }
}

function toggleOpen() {
  open.value = !open.value
  if (open.value) {
    // Navigate to the selected desde month, or current month
    if (props.modelValue.desde) {
      const d = parseISO(props.modelValue.desde)
      viewMonth.value = d.getMonth()
      viewYear.value = d.getFullYear()
    } else {
      viewMonth.value = now.getMonth()
      viewYear.value = now.getFullYear()
    }
    nextTick(() => positionDropdown())
  }
}

// Close on outside click
function onClickOutside(e) {
  if (!open.value) return
  if (containerRef.value?.contains(e.target)) return
  if (dropdownRef.value?.contains(e.target)) return
  open.value = false
}

function onResize() {
  if (open.value) positionDropdown()
}

// Sync view to selection changes
watch(() => props.modelValue.desde, (val) => {
  if (val && open.value) {
    const d = parseISO(val)
    viewMonth.value = d.getMonth()
    viewYear.value = d.getFullYear()
  }
})

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside, true)
  window.addEventListener('resize', onResize)
  window.addEventListener('scroll', onResize, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside, true)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('scroll', onResize, true)
})
</script>
