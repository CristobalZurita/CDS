<template>
    <div class="master-layout">
        <nav class="navbar">
            <div class="nav-brand">
                <span class="logo-text">Cirujano de Sintetizadores</span>
            </div>
            <ul class="nav-links">
                <li><router-link to="/">Inicio</router-link></li>
                <li><router-link to="/dashboard">Dashboard</router-link></li>
            </ul>
        </nav>
        <main class="main-content">
            <router-view />
        </main>
    </div>
</template>

<script setup>
</script>

<style scoped>
.master-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

.navbar {
    background: #333;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand {
    font-size: 1.5rem;
    font-weight: bold;
}

.nav-links {
    display: flex;
    list-style: none;
    gap: 2rem;
    margin: 0;
    padding: 0;
}

.nav-links a {
    color: white;
    text-decoration: none;
}

.nav-links a:hover {
    color: #ccc;
}

.main-content {
    flex: 1;
    padding: 2rem;
    background: #f9f9f9;
}
</style>
