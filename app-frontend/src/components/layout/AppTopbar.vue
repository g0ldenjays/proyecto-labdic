<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useUserStore } from '@/stores/user.store'
import { useAppStore } from '@/stores/app.store'

const router    = useRouter()
const auth      = useAuthStore()
const userStore = useUserStore()
const appStore  = useAppStore()

// Menú de usuario (avatar)
const userMenu = ref()
const userMenuItems = [
  {
    label: 'Mi perfil',
    icon: 'pi pi-user',
    command: () => router.push({ name: 'my-profile' }),
  },
  { separator: true },
  {
    label: 'Cerrar sesión',
    icon: 'pi pi-sign-out',
    command: handleLogout,
  },
]

function toggleUserMenu(event: Event) {
  userMenu.value.toggle(event)
}

function handleLogout() {
  auth.clearToken()
  userStore.clearUser()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="app-topbar">
    <!-- Botón toggle sidebar -->
    <Button
      :icon="appStore.sidebarOpen ? 'pi pi-times' : 'pi pi-bars'"
      text
      rounded
      severity="secondary"
      class="toggle-btn"
      @click="appStore.toggleSidebar()"
      v-tooltip.bottom="appStore.sidebarOpen ? 'Cerrar menú' : 'Abrir menú'"
    />

    <div class="topbar-spacer" />

    <!-- Info del usuario + menú -->
    <div class="user-area">
      <div class="user-info">
        <span class="user-name">{{ userStore.currentUser?.name ?? userStore.currentUser?.username }}</span>
        <span class="user-role">{{ userStore.isAdmin ? 'Administrador' : 'Usuario' }}</span>
      </div>

      <Button
        icon="pi pi-chevron-down"
        text
        rounded
        severity="secondary"
        class="avatar-btn"
        @click="toggleUserMenu"
        aria-haspopup="true"
        aria-controls="user-menu"
      >
        <template #icon>
          <img v-if="userStore.currentUser?.avatarUrl" class="avatar" :src="userStore.currentUser.avatarUrl" :alt="userStore.currentUser.name" />

          <div v-else class="avatar-fallback">
            {{ (userStore.currentUser?.name ?? userStore.currentUser?.username ?? '?')[0].toUpperCase() }}
          </div>
        </template>
      </Button>

      <Menu
        ref="userMenu"
        id="user-menu"
        :model="userMenuItems"
        :popup="true"
      />
    </div>
  </header>
</template>

<style scoped>
.app-topbar {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  border-bottom: 1px solid var(--p-surface-200, rgba(0,0,0,0.08));
  background: var(--p-surface-0, #ffffff);
  gap: 0.5rem;
  flex-shrink: 0;
}

.toggle-btn { color: var(--p-text-muted-color); }
.topbar-spacer { flex: 1; }

/* User area */
.user-area {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.2;
}
.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--p-text-color);
}
.user-role {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
}

/* Avatar */
.avatar,
.avatar-fallback {
  width: 34px;
  height: 34px;
  border-radius: 999px;
}

.avatar {
  object-fit: cover;
  display: block;
}

.avatar-fallback {
  display: grid;
  place-items: center;
  border: 2px solid var(--p-primary-color);
  color: var(--p-primary-color);
  font-weight: 800;
  font-size: 0.9rem;
  background: var(--p-surface-0, #ffffff);
}

/* Ocultar nombre en móvil */
@media (max-width: 640px) {
  .user-info { display: none; }
}
</style>
