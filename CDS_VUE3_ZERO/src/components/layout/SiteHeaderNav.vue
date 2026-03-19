<template>
  <header class="site-header">
    <div class="site-header-inner">
      <router-link to="/" class="brand-link" @click="emit('close-menu')">
        <img
          :src="logoSrc"
          alt="Cirujano de Sintetizadores"
          class="brand-logo"
          width="80"
          height="80"
        />
        <span class="brand-name">Cirujano de Sintetizadores</span>
      </router-link>

      <nav id="primary-nav" class="site-nav" :class="{ 'is-open': menuOpen }">
        <template v-if="isHome">
          <a
            v-for="section in navSections"
            :key="section.id"
            :href="`#${section.id}`"
            class="site-nav-link"
            @click="emit('close-menu')"
          >
            {{ section.name }}
          </a>
        </template>

        <router-link
          v-else
          to="/"
          class="site-nav-link"
          @click="emit('close-menu')"
        >
          Inicio
        </router-link>

        <router-link to="/calculadoras" class="site-nav-link" @click="emit('close-menu')">Calculadoras</router-link>
        <router-link to="/simulador" class="site-nav-link" @click="emit('close-menu')">Simulador</router-link>
        <router-link to="/tienda" class="site-nav-link" @click="emit('close-menu')">Tienda</router-link>

        <router-link
          v-if="isAuthenticated"
          to="/dashboard"
          class="site-nav-link"
          @click="emit('close-menu')"
        >
          Iniciar Sesión
        </router-link>
        <router-link
          v-else
          to="/login"
          class="site-nav-link"
          @click="emit('close-menu')"
        >
          Iniciar Sesión
        </router-link>
      </nav>

      <div class="nav-actions">
        <router-link to="/cotizador" class="nav-cotizar" aria-label="Ir al cotizador">
          <i class="fas fa-file-invoice-dollar"></i>
          <span class="nav-cotizar-label">Cotizar</span>
        </router-link>

        <button
          class="nav-cart-btn"
          type="button"
          aria-label="Carrito de compras"
          @click="emit('cart-click')"
        >
          <i class="fas fa-shopping-cart"></i>
          <span class="nav-cart-label">Carrito</span>
          <span v-if="cartItemsCount > 0" class="nav-cart-badge">
            {{ cartItemsCount }}
          </span>
        </button>

        <button
          class="nav-toggle"
          type="button"
          :aria-expanded="String(menuOpen)"
          aria-controls="primary-nav"
          aria-label="Abrir menú"
          @click="emit('toggle-menu')"
        >
          <i class="fas fa-bars"></i>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  logoSrc: {
    type: String,
    required: true
  },
  menuOpen: {
    type: Boolean,
    default: false
  },
  isHome: {
    type: Boolean,
    default: false
  },
  navSections: {
    type: Array,
    default: () => []
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  cartItemsCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['toggle-menu', 'close-menu', 'cart-click'])
</script>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--cds-dark);
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  --nav-font-size: clamp(2rem, 1rem + 0.24vw, 1.2rem);
  --nav-link-pad-y: clamp(0.56rem, 0.14vw + 0.52rem, 0.68rem);
  --nav-link-pad-x: clamp(0.68rem, 0.14vw + 0.64rem, 0.82rem);
}

.site-header-inner {
  width: 100%;
  max-width: none;
  padding: 0 0.85rem;
  min-height: var(--layout-header-height, var(--cds-header-height, 96px));
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem;
}

.brand-link {
  color: var(--cds-white);
  text-decoration: none;
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.02em;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.brand-logo {
  width: clamp(54px, 4.6vw, 66px);
  height: clamp(54px, 4.6vw, 66px);
  border-radius: var(--cds-radius-sm);
  flex-shrink: 0;
}

.brand-name {
  font-size: clamp(1.5rem, 0.92rem + 0.22vw, 1.12rem);
  line-height: 1.1;
  text-transform: uppercase;
  display: none;
  margin-top: 5px;
}

@media (min-width: 480px) {
  .brand-name {
    display: block;
  }
}

.site-nav {
  display: none;
  flex-wrap: nowrap;
  gap: 0.05rem;
  align-items: center;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
  margin-left: auto;
}

.site-nav.is-open {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--cds-dark);
  padding: 0.75rem 1rem 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  z-index: 99;
}

.site-nav-link {
  color: var(--cds-white);
  text-decoration: none;
  min-height: 50px;
  padding: var(--nav-link-pad-y) var(--nav-link-pad-x);
  border-radius: var(--cds-radius-sm);
  font-size: var(--nav-font-size);
  font-family: var(--cds-font-family-base), sans-serif;
  font-weight: var(--cds-font-medium);
  text-transform: lowercase;
  letter-spacing: 0.01em;
  display: inline-flex;
  align-items: center;
  transition: background 0.15s, color 0.15s, letter-spacing 0.2s ease;
  white-space: nowrap;
}

.site-nav-link:hover,
.site-nav-link.router-link-active:hover {
  background: rgba(236, 107, 0, 0.2);
  letter-spacing: 0.03em;
}

.site-nav-link.router-link-active {
  background: transparent;
}

.nav-cotizar {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.52rem 0.82rem;
  border-radius: var(--cds-radius-sm);
  background: var(--cds-primary);
  color: var(--cds-white);
  text-decoration: none;
  font-size: 0.96rem;
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.02em;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.15s;
}

.nav-cotizar:hover {
  background: #d86100;
  transform: translateY(-1px);
}

.nav-cotizar-label {
  display: none;
}

@media (min-width: 480px) {
  .nav-cotizar-label {
    display: inline;
  }
}

.nav-cart-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 48px;
  padding: 0.5rem 0.8rem;
  border: none;
  border-radius: var(--cds-radius-sm);
  background: rgba(255, 255, 255, 0.12);
  color: var(--cds-white);
  font-size: 0.96rem;
  font-weight: var(--cds-font-semibold);
  letter-spacing: 0.02em;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.12s;
  white-space: nowrap;
}

.nav-cart-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.nav-cart-label {
  display: none;
}

@media (min-width: 480px) {
  .nav-cart-label {
    display: inline;
  }
}

.nav-cart-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 17px;
  height: 17px;
  padding: 0 4px;
  border-radius: var(--cds-radius-pill);
  background: var(--cds-primary);
  color: var(--cds-white);
  font-size: 0.65rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  pointer-events: none;
}

.nav-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border: none;
  border-radius: var(--cds-radius-sm);
  background: transparent;
  color: var(--cds-white);
  font-size: 1.55rem;
  cursor: pointer;
  flex-shrink: 0;
}

.nav-toggle:hover {
  background: rgba(255, 255, 255, 0.15);
}

@media (min-width: 1200px) {
  .site-header-inner {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    justify-content: flex-start;
    gap: 0.35rem;
  }

  .site-nav {
    display: flex;
    position: static;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    flex-wrap: nowrap;
    overflow: visible;
    padding: 0;
    border-top: none;
    gap: 0.05rem;
  }

  .nav-actions {
    margin-left: 0;
    padding-left: 0.25rem;
  }

  .nav-toggle {
    display: none;
  }
}

@media (max-width: 1199px) {
  .site-header-inner {
    gap: 0.5rem;
  }

  .site-nav.is-open {
    display: flex;
  }
}
</style>
