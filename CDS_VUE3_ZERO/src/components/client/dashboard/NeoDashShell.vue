<template>
  <div class="neo-dash-shell">
    <slot name="top" />
    <slot name="nav" />
    <section class="neo-dash-active">
      <slot />
    </section>
  </div>
</template>

<style src="./neoDashboardShared.css"></style>
