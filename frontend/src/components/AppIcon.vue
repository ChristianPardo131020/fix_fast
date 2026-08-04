<template>
  <component :is="icon" class="h-5 w-5" :stroke-width="strokeWidth" aria-hidden="true" />
</template>

<script setup>
import { computed } from 'vue'
import {
  Banknote,
  ChevronLeft,
  ChevronRight,
  CircleCheck,
  CircleDot,
  ClipboardList,
  Clock,
  CreditCard,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  PackageSearch,
  Pencil,
  Plus,
  Search,
  Settings,
  Shield,
  Sun,
  TrendingDown,
  TrendingUp,
  Trash2,
  UserPlus,
  Users,
  Wallet,
  Wrench,
} from '@lucide/vue'

const props = defineProps({
  name: { type: String, default: 'dashboard' },
  strokeWidth: { type: [String, Number], default: 1.8 },
})

const icons = {
  dashboard: LayoutDashboard,
  users: Users,
  orders: ClipboardList,
  payments: CreditCard,
  cash: Banknote,
  settings: Settings,
  plus: Plus,
  search: Search,
  trash: Trash2,
  edit: Pencil,
  menu: Menu,
  logout: LogOut,
  moon: Moon,
  sun: Sun,
  'chevron-left': ChevronLeft,
  'chevron-right': ChevronRight,
  wrench: Wrench,
  wallet: Wallet,
  shield: Shield,
  'user-plus': UserPlus,
  'trend-up': TrendingUp,
  'trend-down': TrendingDown,
  repuesto: PackageSearch,
  dot: CircleDot,
  check: CircleCheck,
  clock: Clock,
}

const icon = computed(() => icons[props.name] || Clock)
</script>
