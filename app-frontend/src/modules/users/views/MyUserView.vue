<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import type { User } from '@/types/user.types'
import { getMyUser } from '@/services/user.service'

const toast   = useToast()
const myUser  = ref<User | null>(null)
const loading = ref(false)
const avatarImageFailed = ref(false)

// Inicial del avatar generada desde el nombre
const avatarInitial = computed(() => {
  if (!myUser.value) return '?'
  return (myUser.value.name ?? myUser.value.username ?? '?')[0].toUpperCase()
})

// Color del avatar basado en el nombre (determinístico)
const avatarColor = computed((): [string, string] => {
  const colors: [string, string][] = [
    ['#4f46e5', '#818cf8'],
    ['#0891b2', '#22d3ee'],
    ['#059669', '#34d399'],
    ['#d97706', '#fbbf24'],
    ['#dc2626', '#f87171'],
    ['#7c3aed', '#a78bfa'],
  ]
  if (!myUser.value) return colors[0]
  const name = myUser.value.name ?? myUser.value.username ?? ''
  const idx  = name.length > 0 ? name.charCodeAt(0) % colors.length : 0
  return colors[idx]
})

const avatarImageUrl = computed(() => {
  if (avatarImageFailed.value) return null
  return myUser.value?.avatarUrl ?? null
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('es-CL', {
    day: '2-digit', month: 'long', year: 'numeric'
  })
}

async function loadMyUser() {
  loading.value = true
  avatarImageFailed.value = false
  try {
    myUser.value = await getMyUser()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron cargar tus datos de usuario.',
      life: 4000,
    })
  } finally {
    loading.value = false
  }
}

function handleAvatarImageError() {
  avatarImageFailed.value = true
}

onMounted(loadMyUser)
</script>

<template>
  <div class="profile-page">

    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem;" />
      <p>Cargando tu perfil...</p>
    </div>

    <template v-else-if="myUser">

      <!-- Hero del perfil -->
      <div class="profile-hero">
        <div class="hero-bg" :style="`background: linear-gradient(135deg, ${avatarColor[0]}22, ${avatarColor[1]}11)`" />

        <div class="hero-content">
          
          <!-- Avatar -->
          <div
            class="avatar-ring"
            :style="`background: linear-gradient(135deg, ${avatarColor[0]}, ${avatarColor[1]})`"
          >
            <img
              v-if="avatarImageUrl"
              class="avatar-image"
              :src="avatarImageUrl"
              :alt="myUser.name"
              @error="handleAvatarImageError"
            />

            <div v-else class="avatar-inner">
              <span class="avatar-letter">{{ avatarInitial }}</span>
            </div>
          </div>

          <!-- Nombre y roles -->
          <div class="hero-info">
            <h1 class="hero-name">{{ myUser.name }}</h1>
            <p class="hero-username">@{{ myUser.username }}</p>
            <div class="hero-roles">
              <span
                v-for="role in myUser.roles"
                :key="role.id"
                class="role-badge"
                :style="`background: ${avatarColor[0]}22; color: ${avatarColor[0]}; border-color: ${avatarColor[0]}44`"
              >
                {{ role.name }}
              </span>
              <span v-if="!myUser.roles?.length" class="role-badge-empty">Sin roles</span>
            </div>
          </div>

          <!-- Estado -->
          <div class="hero-status">
            <span class="status-dot" :class="myUser.isActive ? 'active' : 'inactive'" />
            <span class="status-text">{{ myUser.isActive ? 'Cuenta activa' : 'Cuenta inactiva' }}</span>
          </div>
        </div>
      </div>

      <!-- Grid de información -->
      <div class="info-grid">

        <!-- Información personal -->
        <div class="info-card">
          <div class="card-header">
            <i class="pi pi-user card-icon" />
            <h2 class="card-title">Información personal</h2>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="info-label">RUT</span>
              <span class="info-value">{{ myUser.rut }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Correo</span>
              <span class="info-value break-all">{{ myUser.email }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Teléfono</span>
              <span class="info-value">{{ myUser.phone ?? '—' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Dirección</span>
              <span class="info-value">{{ myUser.address ?? '—' }}</span>
            </div>
          </div>
        </div>

        <!-- Información de cuenta -->
        <div class="info-card">
          <div class="card-header">
            <i class="pi pi-shield card-icon" />
            <h2 class="card-title">Cuenta</h2>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="info-label">Usuario</span>
              <span class="info-value mono">{{ myUser.username }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Tipo</span>
              <span class="info-value">{{ myUser.isAdmin ? 'Administrador' : 'Usuario' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Miembro desde</span>
              <span class="info-value">{{ formatDate(myUser.createdAt) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Estado</span>
              <span class="info-value">
                <span class="status-inline" :class="myUser.isActive ? 'active' : 'inactive'">
                  {{ myUser.isActive ? 'Activo' : 'Inactivo' }}
                </span>
              </span>
            </div>
          </div>
        </div>

      </div>

      <!-- Acción -->
      <div class="profile-actions">
        <Button
          label="Actualizar datos"
          icon="pi pi-refresh"
          severity="secondary"
          outlined
          size="small"
          :loading="loading"
          @click="loadMyUser"
        />
      </div>

    </template>

    <div v-else class="empty-state">
      <i class="pi pi-user-minus" style="font-size: 3rem; opacity: 0.3" />
      <p>No se encontraron datos de usuario.</p>
    </div>

  </div>
</template>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 860px;
  margin: 0 auto;
  width: 100%;
}

/* Loading y empty */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 4rem;
  color: var(--p-text-muted-color);
}

/* Hero */
.profile-hero {
  position: relative;
  border-radius: 16px;
  border: 1px solid var(--p-surface-200, rgba(0,0,0,0.08));
  overflow: hidden;
  background: var(--p-surface-0, #fff);
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  flex-wrap: wrap;
}

/* Avatar */
.avatar-ring {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  padding: 3px;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.avatar-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--p-surface-0, #fff);
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  display: block;
  background: var(--p-surface-0, #fff);
}
.avatar-letter {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  background: v-bind('`linear-gradient(135deg, ${avatarColor[0]}, ${avatarColor[1]})`');
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Info hero */
.hero-info {
  flex: 1;
  min-width: 0;
}
.hero-name {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
  line-height: 1.2;
  color: var(--p-text-color);
}
.hero-username {
  font-size: 0.9rem;
  color: var(--p-text-muted-color);
  margin: 0.2rem 0 0.6rem;
  font-family: 'Courier New', monospace;
}
.hero-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.role-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid;
  text-transform: capitalize;
  letter-spacing: 0.02em;
}
.role-badge-empty {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
  font-style: italic;
}

/* Estado hero */
.hero-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  background: var(--p-surface-50, rgba(0,0,0,0.03));
  border: 1px solid var(--p-surface-200, rgba(0,0,0,0.06));
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.status-dot.active   { background: #22c55e; box-shadow: 0 0 6px #22c55e88; }
.status-dot.inactive { background: #ef4444; }
.status-text { font-size: 0.8rem; font-weight: 500; color: var(--p-text-muted-color); }

/* Grid de cards */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.info-card {
  background: var(--p-surface-0, #fff);
  border: 1px solid var(--p-surface-200, rgba(0,0,0,0.08));
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1rem 1.25rem 0.75rem;
  border-bottom: 1px solid var(--p-surface-100, rgba(0,0,0,0.05));
}
.card-icon {
  font-size: 0.9rem;
  color: var(--p-text-muted-color);
}
.card-title {
  font-size: 0.875rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--p-text-muted-color);
}

.card-body {
  padding: 0.5rem 0;
}

.info-row {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  padding: 0.6rem 1.25rem;
  border-bottom: 1px solid var(--p-surface-50, rgba(0,0,0,0.03));
  transition: background 120ms;
}
.info-row:last-child { border-bottom: none; }
.info-row:hover { background: var(--p-surface-50, rgba(0,0,0,0.02)); }

.info-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--p-text-muted-color);
  min-width: 90px;
  flex-shrink: 0;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.info-value {
  font-size: 0.9rem;
  color: var(--p-text-color);
  min-width: 0;
  word-break: break-word;
}
.info-value.mono { font-family: 'Courier New', monospace; font-size: 0.85rem; }

.status-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  font-weight: 600;
}
.status-inline.active   { color: #16a34a; }
.status-inline.inactive { color: #dc2626; }
.status-inline.active::before  { content: '●'; font-size: 0.6rem; }
.status-inline.inactive::before{ content: '●'; font-size: 0.6rem; }

/* Acciones */
.profile-actions {
  display: flex;
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 640px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .hero-content {
    padding: 1.25rem;
    gap: 1rem;
  }

  .hero-name { font-size: 1.25rem; }

  .avatar-ring {
    width: 64px;
    height: 64px;
  }
  .avatar-letter { font-size: 1.6rem; }

  .hero-status {
    width: 100%;
    justify-content: center;
  }
}
</style>
