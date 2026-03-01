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
const props = defineProps({
  events: { type: Array, default: () => [] }
})

const formatDate = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}
</script>

<style lang="scss" scoped>
@use '@/scss/core' as *;

.timeline {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.75rem;
}

.event {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

.dot {
  width: 10px;
  height: 10px;
  background: $color-link-blue-legacy;
  border-radius: 50%;
  margin-top: 0.35rem;
}

.event-title {
  margin: 0;
  font-weight: $fw-semibold;
}

.event-time {
  margin: 0.15rem 0 0;
  color: $color-gray-500-legacy;
  font-size: $text-sm;
}

.empty {
  color: $color-gray-500-legacy;
}
</style>
