<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <!-- Logo oficial desde /public/images/logo/ -->
        <img
          src="/images/logo/NUEVO_cirujano.png"
          alt="Cirujano de Sintetizadores"
          class="login-logo"
        />
        <h1>Iniciar Sesión</h1>
      </div>

      <LoginForm />

      <div class="login-back">
        <router-link to="/" class="login-back-link">VOLVER AL INICIO</router-link>
      </div>
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

  .login-logo {
    max-width: 280px;
    width: 100%;
    height: auto;
    margin-bottom: 1.5rem;
  }

  h1 {
    font-family: 'Cervo Extrabold', 'Cervo Neue', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: #3e3c38; /* Vintage Black */
    margin-bottom: 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
}

.login-back {
  margin-top: 2rem;
  text-align: center;
}

.login-back-link {
  font-family: 'Cervo Neue', 'Cervo Extrabold', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #ec6b00; /* Orange */
  text-decoration: none;
}

.login-back-link:hover {
  color: #c95800;
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
