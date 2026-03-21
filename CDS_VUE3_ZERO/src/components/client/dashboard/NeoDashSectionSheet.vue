<template>
  <transition name="neo-dash-sheet-fade">
    <div
      v-if="open"
      class="neo-dash-sheet-backdrop"
      role="presentation"
      @click="$emit('close')"
    >
      <section
        class="neo-dash-sheet"
        role="dialog"
        aria-modal="true"
        aria-label="Cambiar sección del dashboard"
        @click.stop
      >
        <header class="neo-dash-sheet-head">
          <div>
            <p class="neo-dash-sheet-eyebrow">Secciones</p>
            <h2 class="neo-dash-sheet-title">Cambiar vista</h2>
          </div>
          <button class="neo-dash-sheet-close" type="button" @click="$emit('close')">
            <i class="fa-solid fa-xmark"></i>
            <span class="sr-only">Cerrar</span>
          </button>
        </header>

        <div class="neo-dash-sheet-grid">
          <button
            v-for="section in sections"
            :key="section.key"
            type="button"
            class="neo-dash-sheet-option"
            :class="{ 'neo-dash-sheet-option--active': section.key === activeSection }"
            :style="{ '--neo-section-accent': section.accent || '#4d4a47' }"
            @click="$emit('select', section.key)"
          >
            <span class="neo-dash-sheet-option-icon">
              <i :class="section.icon"></i>
            </span>
            <span class="neo-dash-sheet-option-copy">
              <strong>{{ section.label }}</strong>
              <small>{{ section.title }}</small>
            </span>
          </button>
        </div>
      </section>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  sections: {
    type: Array,
    default: () => [],
  },
  activeSection: {
    type: String,
    default: 'overview',
  },
})

defineEmits(['close', 'select'])
</script>

<style src="./neoDashboardShared.css"></style>
