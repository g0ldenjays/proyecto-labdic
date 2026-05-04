<!-- src/components/dialogs/UserDetailsDialog.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import type { User } from '@/types/user.types'

interface Props {
  modelValue: boolean
  user: User | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

function close() {
  visible.value = false
}

function formatDate(dateStr: string | null | undefined) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <Drawer
    v-model:visible="visible"
    header="Detalle del usuario"
    position="right"
    style="width: 440px"
  >
    <div v-if="loading" class="py-12 text-center text-muted-color">
      <i class="pi pi-spin pi-spinner text-2xl" />
      <p class="mt-2">Cargando detalle...</p>
    </div>

    <div v-else-if="user" class="drawer-content">
      <!-- Cabecera -->
      <div class="user-header">
        <div class="user-main">
          <span class="user-name">{{ user.name }}</span>
          <span class="user-username">@{{ user.username }}</span>
        </div>

        <div class="user-tags">
          <Tag
            :value="user.isActive ? 'Activo' : 'Inactivo'"
            :severity="user.isActive ? 'success' : 'danger'"
          />
          <Tag v-if="user.isAdmin" value="Administrador" severity="contrast" />
        </div>
      </div>

      <!-- Información general -->
      <div class="section-title">Información general</div>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">RUT</span>
          <span class="info-value">{{ user.rut || '—' }}</span>
        </div>

        <div class="info-item">
          <span class="info-label">Correo</span>
          <span class="info-value">{{ user.email || '—' }}</span>
        </div>

        <div class="info-item">
          <span class="info-label">Teléfono</span>
          <span class="info-value">{{ user.phone || '—' }}</span>
        </div>

        <div class="info-item">
          <span class="info-label">Dirección</span>
          <span class="info-value">{{ user.address || '—' }}</span>
        </div>
      </div>

      <!-- Roles -->
      <div class="section-title">Roles</div>
      <div class="roles-wrap">
        <Tag v-for="role in user.roles" :key="role.id" :value="role.name" severity="secondary" />
        <span v-if="!user.roles?.length" class="empty-text"> Sin roles asignados </span>
      </div>

      <!-- Metadatos -->
      <div class="section-title">Metadatos</div>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">ID</span>
          <span class="info-value">#{{ user.id }}</span>
        </div>

        <div class="info-item">
          <span class="info-label">Creado</span>
          <span class="info-value">{{ formatDate(user.createdAt) }}</span>
        </div>
      </div>

      <!-- Acción -->
      <div class="drawer-actions">
        <Button label="Cerrar" icon="pi pi-times" severity="secondary" text @click="close" />
      </div>
    </div>
  </Drawer>
</template>

<style scoped>
.drawer-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 0.25rem 0;
}

.user-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.user-main {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.user-name {
  font-size: 1.125rem;
  font-weight: 700;
}

.user-username {
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
}

.user-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.section-title {
  font-weight: 700;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--p-text-muted-color);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.85rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.info-label {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.info-value {
  font-size: 0.95rem;
  word-break: break-word;
}

.roles-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.empty-text {
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
  font-style: italic;
}

.drawer-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.5rem;
}
</style>
