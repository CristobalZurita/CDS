<template>
  <div class="wizard-section-bar">
    <nav class="section-tabs">
      <a
        v-for="(section, idx) in sections"
        :key="section.id"
        :href="`#${section.id}`"
        class="section-tab"
        :class="{
          'is-active': activeSection === section.id,
          'is-past': activeSectionIndex > idx
        }"
        @click.prevent="$emit('navigate', section.id)"
      >{{ section.label }}</a>
    </nav>

    <div class="wizard-bar-meta">
      <span class="bar-progress">{{ progress }}%</span>
      <div v-if="nextClientCode" class="bar-code">
        <span class="bar-code-label">CL</span>
        <span class="bar-code-value">{{ nextClientCode }}</span>
      </div>
      <div v-if="nextOtCode" class="bar-code">
        <span class="bar-code-label">OT</span>
        <span class="bar-code-value">{{ nextOtCode }}</span>
      </div>
    </div>

    <div class="section-fill-track">
      <div class="section-fill"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'

const props = defineProps({
  sections: {
    type: Array,
    default: () => []
  },
  activeSection: {
    type: String,
    default: ''
  },
  progress: {
    type: Number,
    default: 0
  },
  nextClientCode: {
    type: String,
    default: ''
  },
  nextOtCode: {
    type: String,
    default: ''
  }
})

defineEmits(['navigate'])

const activeSectionIndex = computed(() => {
  const idx = props.sections.findIndex(s => s.id === props.activeSection)
  return idx >= 0 ? idx : 0
})

// Fill basado en scroll real del contenedor admin-content
const scrollProgress = ref(0)
let scrollEl = null

function onScroll() {
  if (!scrollEl) return
  const max = scrollEl.scrollHeight - scrollEl.clientHeight
  scrollProgress.value = max > 0 ? (scrollEl.scrollTop / max) * 100 : 0
}

onMounted(() => {
  scrollEl = document.querySelector('.admin-content')
  if (scrollEl) scrollEl.addEventListener('scroll', onScroll, { passive: true })
})

onBeforeUnmount(() => {
  if (scrollEl) scrollEl.removeEventListener('scroll', onScroll)
})

const fillScale = computed(() => String(scrollProgress.value / 100))
</script>

<style scoped>
.wizard-section-bar {
  position: sticky;
  top: 0;
  z-index: 48;
  background: var(--cds-white);
  border-bottom: 1px solid var(--cds-border-card);
  display: flex;
  align-items: stretch;
  gap: 0;
  margin-bottom: var(--intake-header-margin-bottom, 1.5rem);
  /* bleed to edges of admin-content */
  margin-left: calc(-1 * var(--admin-space-2xl, 3.3rem));
  margin-right: calc(-1 * var(--admin-space-2xl, 3.3rem));
  padding-left: var(--admin-space-2xl, 3.3rem);
  padding-right: var(--admin-space-2xl, 3.3rem);
}

.section-tabs {
  flex: 1;
  display: flex;
  align-items: stretch;
  overflow-x: auto;
  scrollbar-width: none;
}

.section-tabs::-webkit-scrollbar {
  display: none;
}

.section-tab {
  padding: 0.75rem 1.1rem;
  font-size: var(--cds-text-sm);
  font-weight: 500;
  color: var(--cds-text-muted);
  text-decoration: none;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
  display: flex;
  align-items: center;
}

.section-tab:hover {
  color: var(--cds-text-normal);
}

.section-tab.is-past {
  color: var(--cds-text-normal);
}

.section-tab.is-active {
  color: var(--cds-primary);
  border-bottom-color: var(--cds-primary);
  font-weight: 600;
}

.wizard-bar-meta {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
  padding: 0.5rem 0;
}

.bar-progress {
  font-size: var(--cds-text-sm);
  font-weight: 700;
  color: var(--cds-primary);
  white-space: nowrap;
  min-width: 3.5rem;
  text-align: right;
}

.bar-code {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.55rem;
  background: var(--cds-light-1, #f0ede3);
  border-radius: var(--cds-radius-sm);
}

.bar-code-label {
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--cds-text-muted);
  font-weight: 700;
}

.bar-code-value {
  font-size: var(--cds-text-sm);
  font-weight: 700;
  color: var(--cds-primary);
  font-family: var(--cds-font-family-mono, monospace);
}

/* Orange scroll fill — bottom edge of bar */
.section-fill-track {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: var(--cds-light-2, #e8e6dd);
  overflow: hidden;
}

.section-fill {
  height: 100%;
  width: 100%;
  background: var(--cds-primary);
  transform: scaleX(v-bind(fillScale));
  transform-origin: left center;
  transition: transform 0.35s ease;
}

@media (max-width: 768px) {
  .wizard-section-bar {
    position: relative;
  }

  .wizard-bar-meta {
    display: none;
  }

  .section-tab {
    padding: 0.6rem 0.75rem;
    font-size: var(--cds-text-xs);
  }
}
</style>
