<template>
  <RouterView />
  <ToastHost />
  <ConfirmDialog />
</template>

<script setup>
import ConfirmDialog from './components/ConfirmDialog.vue'
import ToastHost from './components/ToastHost.vue'
</script>
