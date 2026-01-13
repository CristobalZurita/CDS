<template>
    <div class="home-page">
        <h1>Bienvenido a Cirujano de Sintetizadores</h1>
        <p>Un taller especializado en reparación y restauración de sintetizadores.</p>
        <router-link to="/agendar" class="btn btn-primary">Agendar cita</router-link>
    </div>
</template>

<script setup>
</script>

<style scoped>
.home-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    text-align: center;
}

h1 {
    font-size: 2rem;
    margin: 0;
}

p {
    font-size: 1.1rem;
    color: #666;
}

.btn {
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    text-decoration: none;
    display: inline-block;
    font-weight: bold;
    transition: all 0.3s;
}

.btn-primary {
    background: #007bff;
    color: white;
}

.btn-primary:hover {
    background: #0056b3;
}
</style>