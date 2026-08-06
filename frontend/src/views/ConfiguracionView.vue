<template>
  <div class="space-y-6">
    <PageHeader title="Configuracion" subtitle="Preferencias del frontend y datos de despliegue." />

    <BaseCard title="Conexion API" subtitle="Lista para usar en local o Netlify con variables de entorno.">
      <div class="grid gap-4 md:grid-cols-2">
        <div class="rounded-xl bg-slate-50 p-4 dark:bg-slate-800/60">
          <p class="text-sm font-medium text-slate-500">Base URL</p>
          <p class="mt-2 break-all font-mono text-sm text-slate-950 dark:text-white">{{ apiUrl }}</p>
        </div>
        <div class="rounded-xl bg-slate-50 p-4 dark:bg-slate-800/60">
          <p class="text-sm font-medium text-slate-500">Variable Netlify</p>
          <p class="mt-2 font-mono text-sm text-slate-950 dark:text-white">VITE_API_URL</p>
        </div>
      </div>
    </BaseCard>

    <BaseCard title="Apariencia" subtitle="Preferencias locales del navegador.">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="font-medium text-slate-950 dark:text-white">Modo oscuro</p>
          <p class="text-sm text-slate-500">Cambia el contraste del panel administrativo.</p>
        </div>
        <BaseButton variant="secondary" icon="moon" @click="ui.toggleTheme">{{ ui.darkMode ? 'Usar claro' : 'Usar oscuro' }}</BaseButton>
      </div>
    </BaseCard>

    <BaseCard title="Sesion" subtitle="JWT almacenado localmente para consumir FastAPI.">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-slate-500">Puedes cerrar sesion para limpiar el token del navegador.</p>
        <BaseButton variant="danger" icon="logout" @click="auth.logout()">Cerrar sesion</BaseButton>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import BaseButton from '../components/BaseButton.vue'
import BaseCard from '../components/BaseCard.vue'
import PageHeader from '../components/PageHeader.vue'
import { API_BASE_URL } from '../api/http'
import { useAuthStore } from '../stores/auth'
import { useUiStore } from '../stores/ui'

const apiUrl = API_BASE_URL
const auth = useAuthStore()
const ui = useUiStore()
</script>
