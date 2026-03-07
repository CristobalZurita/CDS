<template>
  <ol class="timeline">
    <li v-for="event in events" :key="event.id || event.timestamp" class="event">
      <div class="dot"></div>
      <div>
        <p class="event-title">{{ event.title || event.status }}</p>
        <p class="event-time">{{ formatDate(event.timestamp || event.created_at) }}</p>
      </div>
    </li>
    <li v-if="!events.length" class="empty">Sin eventos registrados.</li>
  </ol>
</template>

<script setup>
const _props = defineProps({
  events: { type: Array, default: () => [] }
})

const formatDate = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}
</script>
