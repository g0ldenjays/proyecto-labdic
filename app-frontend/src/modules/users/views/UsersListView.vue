<script setup lang="ts">
import { getUsers, createUser, updateUser, deleteUser, getUser } from '@/services/user.service'
import type { User, NewUserPayload } from '@/types/user.types'
import { ref, type Ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user.store'
import { useToast } from 'primevue/usetoast'
import UserForm from '@/modules/users/components/UserForm.vue'
import UserDetailsDialog from '@/modules/users/components/UserDetailsDialog.vue'
import UserDeleteConfirmDialog from '@/modules/users/components/UserDeleteConfirmDialog.vue'

const userStore = useUserStore()
const toast = useToast()

// ── Cargar usuarios ───────────────────────────────────────────────────
const loading = ref(false)
const users: Ref<User[]> = ref([])

async function loadUsers() {
  loading.value = true
  try {
    users.value = await getUsers()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error al cargar',
      detail: 'No se pudieron cargar los usuarios. Intenta nuevamente.',
      life: 4000,
    })
  } finally {
    loading.value = false
  }
}

// ── Ver detalles ──────────────────────────────────────────────────────
const showDetailsDrawer = ref(false)
const detailsLoading = ref(false)
const selectedUser: Ref<User | null> = ref(null)

async function viewDetails(user: User) {
  showDetailsDrawer.value = true
  detailsLoading.value = true

  try {
    selectedUser.value = await getUser(user.id)
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el detalle del usuario.',
      life: 4000,
    })
    showDetailsDrawer.value = false
  } finally {
    detailsLoading.value = false
  }
}

// ── Eliminar usuario ──────────────────────────────────────────────────
const showDeleteDialog = ref(false)
const userToDelete: Ref<User | null> = ref(null)

function confirmDelete(user: User) {
  userToDelete.value = user
  showDeleteDialog.value = true
}

async function handleDelete() {
  if (!userToDelete.value) return
  try {
    await deleteUser(userToDelete.value.id)
    users.value = users.value.filter((u) => u.id !== userToDelete.value!.id)
    toast.add({
      severity: 'success',
      summary: 'Usuario eliminado',
      detail: `Se eliminó a "${userToDelete.value.username}".`,
      life: 3000,
    })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error al eliminar',
      detail: 'No se pudo eliminar el usuario.',
      life: 4000,
    })
  } finally {
    showDeleteDialog.value = false
    userToDelete.value = null
  }
}

// ── Drawer crear / editar ─────────────────────────────────────────────
type DrawerMode = 'create' | 'edit'

const showDrawer = ref(false)
const drawerMode = ref<DrawerMode>('create')
const drawerLoading = ref(false)
const submitting = ref(false)

const emptyForm: NewUserPayload = {
  username: '',
  rut: '',
  name: '',
  email: '',
  phone: '',
  address: '',
  password: '',
  isAdmin: false,
  roleIds: [],
}
const drawerForm = ref<NewUserPayload>({ ...emptyForm })
const editingUserId = ref<number | null>(null)

function openCreateDrawer() {
  drawerMode.value = 'create'
  editingUserId.value = null
  drawerForm.value = { ...emptyForm }
  showDrawer.value = true
}

async function openEditDrawer(user: User) {
  drawerMode.value = 'edit'
  editingUserId.value = user.id
  showDrawer.value = true
  drawerLoading.value = true

  try {
    const u = await getUser(user.id)
    drawerForm.value = {
      username: u.username,
      rut: u.rut,
      name: u.name,
      email: u.email,
      phone: u.phone,
      address: u.address,
      isAdmin: u.isAdmin,
      password: '', // nunca se trae del backend
      roleIds: u.roles.map((r) => r.id),
    }
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el usuario para editar.',
      life: 4000,
    })
    showDrawer.value = false
  } finally {
    drawerLoading.value = false
  }
}

function closeDrawer() {
  showDrawer.value = false
}

async function handleSubmit(payload: NewUserPayload) {
  submitting.value = true
  try {
    if (drawerMode.value === 'create') {
      const newUser = await createUser(payload)
      users.value.push(newUser)
      toast.add({
        severity: 'success',
        summary: 'Usuario creado',
        detail: `Se creó "${payload.username}" correctamente.`,
        life: 3000,
      })
    } else {
      // Edit: no enviamos password si está vacío
      const toSend: Partial<NewUserPayload> = { ...payload }
      if (!toSend.password?.trim()) delete toSend.password

      const updated = await updateUser(editingUserId.value!, toSend)

      // Actualizar en memoria sin recargar toda la lista
      const idx = users.value.findIndex((u) => u.id === editingUserId.value)
      if (idx !== -1) users.value[idx] = updated

      toast.add({
        severity: 'success',
        summary: 'Usuario actualizado',
        detail: `Se actualizaron los datos de "${payload.username}".`,
        life: 3000,
      })
    }

    showDrawer.value = false
  } catch {
    toast.add({
      severity: 'error',
      summary: drawerMode.value === 'create' ? 'Error al crear' : 'Error al actualizar',
      detail: 'No se pudo completar la operación. Intenta nuevamente.',
      life: 4000,
    })
  } finally {
    submitting.value = false
  }
}

// ── Init ──────────────────────────────────────────────────────────────
onMounted(loadUsers)
</script>

<template>
  <div class="page-container">
    <!-- Cabecera de la página -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Usuarios</h1>
        <p class="page-subtitle">Gestiona los usuarios del sistema</p>
      </div>
      <Button
        v-if="userStore.canManageUsers"
        icon="pi pi-plus"
        label="Nuevo Usuario"
        @click="openCreateDrawer"
      />
    </div>

    <!-- Tabla de usuarios -->
    <Card>
      <template #content>
        <DataTable :value="users" :loading="loading" dataKey="id" stripedRows>
          <Column field="username" header="Usuario" />
          <Column field="name" header="Nombre" />
          <Column field="phone" header="Teléfono" />

          <Column field="isActive" header="Estado">
            <template #body="{ data }">
              <Tag
                :value="data.isActive ? 'Activo' : 'Inactivo'"
                :severity="data.isActive ? 'success' : 'danger'"
              />
            </template>
          </Column>

          <Column header="Roles">
            <template #body="{ data }">
              <div class="flex gap-1 flex-wrap">
                <Tag
                  v-for="role in data.roles"
                  :key="role.id"
                  :value="role.name"
                  severity="secondary"
                />
              </div>
            </template>
          </Column>

          <Column header="Acciones" style="width: 120px">
            <template #body="{ data }">
              <Button
                icon="pi pi-info-circle"
                rounded
                text
                severity="info"
                v-tooltip.top="'Ver detalles'"
                @click="viewDetails(data)"
              />
              <Button
                v-if="userStore.canManageUsers"
                icon="pi pi-pencil"
                rounded
                text
                severity="secondary"
                v-tooltip.top="'Editar'"
                @click="openEditDrawer(data)"
              />
              <Button
                v-if="userStore.canManageUsers"
                icon="pi pi-trash"
                rounded
                text
                severity="danger"
                v-tooltip.top="'Eliminar'"
                @click="confirmDelete(data)"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Drawer crear / editar usuario -->
    <Drawer
      v-model:visible="showDrawer"
      :header="drawerMode === 'create' ? 'Nuevo usuario' : 'Editar usuario'"
      position="right"
      style="width: 440px"
      :dismissable="!submitting"
    >
      <div v-if="drawerLoading" class="py-12 text-center text-muted-color">
        <i class="pi pi-spin pi-spinner text-2xl" />
        <p class="mt-2">Cargando datos...</p>
      </div>

      <UserForm
        v-else
        :model-value="drawerForm"
        :submitting="submitting"
        :mode="drawerMode"
        @submit="handleSubmit"
        @cancel="closeDrawer"
      />
    </Drawer>

    <!-- Drawer Detalles -->
    <UserDetailsDialog v-model="showDetailsDrawer" :user="selectedUser" :loading="detailsLoading" />
    <!-- Dialog -->
    <UserDeleteConfirmDialog
      v-model="showDeleteDialog"
      :user="userToDelete"
      @confirm="handleDelete"
    />
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}
.page-subtitle {
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
  margin: 0.25rem 0 0;
}
</style>
