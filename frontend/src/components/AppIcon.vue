<template>
  <span class="inline-flex h-5 w-5 items-center justify-center" aria-hidden="true">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="h-full w-full">
      <template v-if="name === 'dashboard'">
        <path d="M4 13h6V4H4v9Z" /><path d="M14 20h6V4h-6v16Z" /><path d="M4 20h6v-3H4v3Z" />
      </template>
      <template v-else-if="name === 'users'">
        <path d="M16 19c0-2.2-1.8-4-4-4H8c-2.2 0-4 1.8-4 4" /><circle cx="10" cy="8" r="4" /><path d="M20 18c0-1.8-1.1-3.4-2.7-4" /><path d="M16.5 4.4a4 4 0 0 1 0 7.2" />
      </template>
      <template v-else-if="name === 'orders'">
        <path d="M7 3h10l3 3v15H4V3h3Z" /><path d="M8 11h8" /><path d="M8 15h5" /><path d="M16 3v4h4" />
      </template>
      <template v-else-if="name === 'payments'">
        <rect x="3" y="5" width="18" height="14" rx="3" /><path d="M3 10h18" /><path d="M7 15h3" />
      </template>
      <template v-else-if="name === 'cash'">
        <path d="M4 8h16v10H4z" /><path d="M7 8V5h10v3" /><circle cx="12" cy="13" r="2.5" />
      </template>
      <template v-else-if="name === 'settings'">
        <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.2 2.2-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V21h-3v-.6a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1-2.2-2.2.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H3v-3h.6a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1 2.2-2.2.1.1a1.7 1.7 0 0 0 1.9.3 1.7 1.7 0 0 0 1-1.6V3h3v.6a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1 2.2 2.2-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.6v3h-.6a1.7 1.7 0 0 0-1.6 1Z" />
      </template>
      <template v-else-if="name === 'plus'">
        <path d="M12 5v14" /><path d="M5 12h14" />
      </template>
      <template v-else-if="name === 'search'">
        <circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
      </template>
      <template v-else-if="name === 'trash'">
        <path d="M4 7h16" /><path d="M10 11v6" /><path d="M14 11v6" /><path d="M6 7l1 14h10l1-14" /><path d="M9 7V4h6v3" />
      </template>
      <template v-else-if="name === 'edit'">
        <path d="M4 20h4l11-11a2.8 2.8 0 0 0-4-4L4 16v4Z" /><path d="m13.5 6.5 4 4" />
      </template>
      <template v-else-if="name === 'menu'">
        <path d="M4 7h16" /><path d="M4 12h16" /><path d="M4 17h16" />
      </template>
      <template v-else-if="name === 'logout'">
        <path d="M10 17l5-5-5-5" /><path d="M15 12H3" /><path d="M21 3v18" />
      </template>
      <template v-else-if="name === 'moon'">
        <path d="M21 14.5A8 8 0 1 1 9.5 3 6.5 6.5 0 0 0 21 14.5Z" />
      </template>
      <template v-else>
        <circle cx="12" cy="12" r="9" /><path d="M12 8v4l3 2" />
      </template>
    </svg>
  </span>
</template>

<script setup>
defineProps({
  name: { type: String, default: 'dashboard' },
})
</script>
