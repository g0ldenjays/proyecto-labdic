<script setup lang="ts">
// Layout principal — sidebar + topbar + contenido.
// Usado por todas las rutas privadas.
</script>

<template>
  <div class="app-layout">
    <AppSidebar />

    <div class="app-main">
      <AppTopbar />

      <main class="app-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  overflow: hidden;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* evita overflow del sidebar */
  height: 100vh;
}

.app-content {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}
</style>
