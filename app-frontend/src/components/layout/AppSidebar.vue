<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user.store'
import { useAppStore } from '@/stores/app.store'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()

const baseItems = [
  { label: 'Inicio', icon: 'pi pi-home', name: 'home' },
  { label: 'Catálogo', icon: 'pi pi-box', name: 'catalog' },
  { label: 'Mis Solicitudes', icon: 'pi pi-list', name: 'my-loans' },
]

const adminItems = [
  { label: 'Usuarios', icon: 'pi pi-users', name: 'admin-users' },
  { label: 'Productos', icon: 'pi pi-tag', name: 'admin-products' },
  { label: 'Dispositivos', icon: 'pi pi-server', name: 'admin-devices' },
  { label: 'Préstamos', icon: 'pi pi-file-edit', name: 'admin-loans' },
  { label: 'Auxiliares', icon: 'pi pi-cog', name: 'admin-catalog' },
  { label: 'Admin de Inventario', icon: 'pi pi-chart-bar', name: 'inventory-admin' },
  { label: 'Docs administrativos', icon: 'pi pi-file-pdf', name: 'administrative-documents' },
]

const navItems = computed(() => {
  const items = [...baseItems]
  if (userStore.isAdmin) items.push(...adminItems)
  return items
})

function navigate(name: string) {
  router.push({ name })
  if (window.innerWidth < 768) appStore.sidebarOpen = false
}

function isActive(name: string) {
  if (name === 'admin-products')
    return route.name === 'admin-products' || route.name === 'admin-product-detail'
  return route.name === name
}
</script>

<template>
  <aside class="app-sidebar" :class="{ collapsed: !appStore.sidebarOpen }">
    <div class="sidebar-logo">
      <div class="logo-icon">LD</div>
      <span v-if="appStore.sidebarOpen" class="logo-text">LabDIC</span>
    </div>

    <Divider class="my-2" />

    <nav class="sidebar-nav">
      <button
        v-for="item in navItems"
        :key="item.name"
        class="nav-item"
        :class="{ active: isActive(item.name) }"
        @click="navigate(item.name)"
        v-tooltip.right="!appStore.sidebarOpen ? item.label : undefined"
      >
        <i :class="item.icon" class="nav-icon" />
        <span v-if="appStore.sidebarOpen" class="nav-label">{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 220px;
  height: 100vh;
  background: var(--p-surface-900, #0f172a);
  border-right: 1px solid var(--p-surface-700, rgba(255, 255, 255, 0.08));
  display: flex;
  flex-direction: column;
  padding: 1rem 0.75rem;
  transition: width 200ms ease;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  align-self: flex-start;
}
.app-sidebar.collapsed {
  width: 64px;
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.25rem 0.25rem 0.75rem;
}
.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #4f46e5, #06b6d4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.logo-text {
  font-weight: 700;
  font-size: 1.1rem;
  color: #fff;
  white-space: nowrap;
}
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition:
    background 150ms,
    color 150ms;
  text-align: left;
  white-space: nowrap;
  width: 100%;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.9);
}
.nav-item.active {
  background: rgba(79, 70, 229, 0.25);
  color: #a5b4fc;
}
.nav-icon {
  font-size: 1rem;
  flex-shrink: 0;
  width: 18px;
  text-align: center;
}
.nav-label {
  font-size: 0.9rem;
  font-weight: 500;
}
.collapsed .nav-label,
.collapsed .logo-text {
  display: none;
}
.collapsed .nav-item {
  justify-content: center;
  padding: 0.6rem;
}
</style>
