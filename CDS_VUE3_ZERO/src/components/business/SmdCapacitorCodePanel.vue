<template>
  <section class="calc-panel">
    <div class="panel-header">
      <div class="panel-title">
        <i class="fa-solid fa-hashtag"></i>
        Codigo ceramico / poliester
      </div>
    </div>

    <div class="panel-body">
      <div class="diagram-card cap-visual-card">
        <img
          class="cap-visual-card__image cap-visual-card__image--ceramic"
          src="/images/calculadoras/CAP_C.webp"
          alt="Capacitor ceramico"
        />
      </div>
      <p class="cap-visual-caption">Ceramico (Cap C)</p>

      <div class="form-grid">
        <label class="form-field">
          <span>Codigo</span>
          <input v-model.trim="form.code" type="text" placeholder="Ej: 104 o 472" />
        </label>

        <label class="form-field">
          <span>Tipo</span>
          <select v-model="form.type">
            <option v-for="item in smdCapacitorTypeOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </label>
      </div>

      <div class="form-actions">
        <button type="button" class="action-btn" @click="$emit('reset-code')">
          <i class="fa-solid fa-rotate-left"></i>
          Resetear parametros
        </button>
      </div>

      <div class="output-values">
        <div class="value-row">
          <span>pF</span>
          <strong>{{ isValidCode ? decoded.pf : '-' }}</strong>
        </div>
        <div class="value-row">
          <span>nF</span>
          <strong>{{ isValidCode ? decoded.nf : '-' }}</strong>
        </div>
        <div class="value-row">
          <span>µF</span>
          <strong>{{ isValidCode ? decoded.uf : '-' }}</strong>
        </div>
      </div>

      <p class="result-hint">El codigo se interpreta en pF: dos digitos + cantidad de ceros.</p>
    </div>
  </section>
</template>

<script setup>
defineProps({
  decoded: { type: Object, required: true },
  form: { type: Object, required: true },
  isValidCode: { type: Boolean, default: false },
  smdCapacitorTypeOptions: { type: Array, required: true }
})

defineEmits(['reset-code'])
</script>

<style scoped src="../../pages/calculators/commonCalculatorPage.css"></style>
<style scoped src="./smdCapacitorPageShared.css"></style>
