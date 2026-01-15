<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>Iniciar Sesión</h1>
        <p class="subtitle">Bienvenido a Cirujano de Sintetizadores</p>
      </div>

      <LoginForm />
    </div>
  </div>
</template>

<script setup>
import LoginForm from '@/vue/components/auth/LoginForm.vue'
</script>

<style scoped lang="scss">
/* ===========================================
   LOGINPAGE - Manual de Identidad Visual
   Paleta: Vintage Black #3e3c38, Orange #ec6b00,
           Vintage Beige #d3d0c3, Black #000000
   Tipografía: Cervo Neue, Cervo Extrabold
   =========================================== */

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000000; /* Black - Paleta Secundaria Web */
  padding: 2rem;
}

.login-container {
  background: #d3d0c3; /* Vintage Beige - Paleta Primaria */
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  padding: 3rem 2rem;
  max-width: 500px;
  width: 100%;
  border: 2px solid #3e3c38; /* Vintage Black */
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;

  h1 {
    font-family: 'Cervo Extrabold', 'Cervo Neue', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #3e3c38; /* Vintage Black */
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .subtitle {
    font-family: 'Cervo Neue', sans-serif;
    color: #cc7d43; /* Vintage Orange */
    font-size: 1.05rem;
  }
}

@media (max-width: 768px) {
  .login-page {
    padding: 1rem;
  }

  .login-container {
    padding: 2rem 1.5rem;
  }

  .login-header h1 {
    font-size: 1.5rem;
  }
}
</style>
