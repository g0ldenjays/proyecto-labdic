<script setup lang="ts">
import { ref, onMounted, computed, type Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { Device, DevicePayload } from '@/types/device.types'
import type { Product } from '@/types/product.types'
import type { Status, Ubication } from '@/types/catalog.types'
import {
  getDevices,
  getDevice,
  createDevice,
  updateDevice,
  deleteDevice,
  changeDeviceStatus,
} from '@/services/device.service'
import { getProducts } from '@/services/product.service'
import { getStatuses, getUbications } from '@/services/catalog.service'
import DeviceStatusBadge from '@/components/ui/DevicesStatusBadge.vue'
import DeviceForm from '@/modules/components/DeviceForm.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

// ── Datos ─────────────────────────────────────────────────────────────
const loading = ref(false)
const devices: Ref<Device[]> = ref([])
const products = ref<Product[]>([])
const statuses = ref<Status[]>([])
const ubications = ref<Ubication[]>([])

async function loadDevices() {
  loading.value = true
  try {
    devices.value = await getDevices()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron cargar los dispositivos.',
      life: 4000,
    })
  } finally {
    loading.value = false
  }
}

async function loadAuxData() {
  const [p, s, u] = await Promise.all([getProducts(), getStatuses(), getUbications()])
  products.value = p
  statuses.value = s
  ubications.value = u
}

// ── Filtro por producto (viene de ProductDetailView) ──────────────────
const filterProductId = computed(() => {
  const q = route.query.product
  return q ? Number(q) : null
})

const filteredDevices = computed(() => {
  if (!filterProductId.value) return devices.value
  return devices.value.filter((d) => d.productId === filterProductId.value)
})

const filterProductName = computed(() => {
  if (!filterProductId.value) return null
  return products.value.find((p) => p.id === filterProductId.value)?.name ?? null
})

// ── Drawer crear / editar ─────────────────────────────────────────────
type DrawerMode = 'create' | 'edit'

const showDrawer = ref(false)
const drawerMode = ref<DrawerMode>('create')
const drawerLoading = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)

function getEmptyForm(): DevicePayload {
  return {
    productId: filterProductId.value ?? 0,
    statusId: 0,
    internalCode: null,
    serialNumber: null,
    ubicationId: null,
  }
}
const drawerInitialValues = ref<DevicePayload>(getEmptyForm())

function openCreateDrawer() {
  drawerMode.value = 'create'
  editingId.value = null
  originalStatusId.value = 0
  drawerInitialValues.value = getEmptyForm()
  showDrawer.value = true
}

const originalStatusId = ref<number>(0)

async function openEditDrawer(device: Device) {
  drawerMode.value = 'edit'
  editingId.value = device.id
  showDrawer.value = true
  drawerLoading.value = true

  try {
    const d = await getDevice(device.id)

    drawerInitialValues.value = {
      productId: d.productId,
      statusId: d.statusId,
      internalCode: d.internalCode ?? null,
      serialNumber: d.serialNumber ?? null,
      ubicationId: d.ubicationId ?? null,
    }

    originalStatusId.value = d.statusId
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el dispositivo.',
      life: 4000,
    })
    showDrawer.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function handleSubmit(payload: DevicePayload) {
  if (!payload.productId || !payload.statusId) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'El producto y el estado son obligatorios.',
      life: 3000,
    })
    return
  }

  const normalizedPayload: DevicePayload = {
    productId: payload.productId,
    statusId: payload.statusId,
    internalCode: payload.internalCode || null,
    serialNumber: payload.serialNumber || null,
    ubicationId: payload.ubicationId || null,
  }

  submitting.value = true
  try {
    if (drawerMode.value === 'create') {
      const newDevice = await createDevice(normalizedPayload)
      devices.value.push(newDevice)

      toast.add({
        severity: 'success',
        summary: 'Dispositivo creado',
        detail: 'El dispositivo fue registrado correctamente.',
        life: 3000,
      })
    } else {
      if (normalizedPayload.statusId !== originalStatusId.value) {
        await changeDeviceStatus(editingId.value!, normalizedPayload.statusId)
      }

      const updated = await updateDevice(editingId.value!, normalizedPayload)

      const idx = devices.value.findIndex(d => d.id === editingId.value)
      if (idx !== -1) {
        devices.value[idx] = {
          ...updated,
          status: statuses.value.find(s => s.id === normalizedPayload.statusId) ?? updated.status,
          statusId: normalizedPayload.statusId,
        }
      }

      toast.add({
        severity: 'success',
        summary: 'Dispositivo actualizado',
        detail: 'Los datos fueron actualizados correctamente.',
        life: 3000,
      })
    }

    showDrawer.value = false
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo completar la operación.',
      life: 4000,
    })
  } finally {
    submitting.value = false
  }
}

// ── Eliminar ──────────────────────────────────────────────────────────
const showDeleteDialog = ref(false)
const deviceToDelete: Ref<Device | null> = ref(null)

function confirmDelete(device: Device) {
  deviceToDelete.value = device
  showDeleteDialog.value = true
}

async function handleDelete() {
  if (!deviceToDelete.value) return
  try {
    await deleteDevice(deviceToDelete.value.id)
    devices.value = devices.value.filter((d) => d.id !== deviceToDelete.value!.id)
    toast.add({
      severity: 'success',
      summary: 'Eliminado',
      detail: 'El dispositivo fue eliminado correctamente.',
      life: 3000,
    })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo eliminar el dispositivo.',
      life: 4000,
    })
  } finally {
    showDeleteDialog.value = false
    deviceToDelete.value = null
  }
}

// ── Init ──────────────────────────────────────────────────────────────
onMounted(() => {
  loadDevices()
  loadAuxData()
})
</script>

<template>
  <div class="page-container">
    <!-- Cabecera -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Dispositivos</h1>
        <p v-if="filterProductName" class="page-subtitle">
          Filtrando por producto: <strong>{{ filterProductName }}</strong>
          <Button
            icon="pi pi-times"
            text
            rounded
            size="small"
            v-tooltip.top="'Quitar filtro'"
            @click="router.replace({ name: 'admin-devices' })"
          />
        </p>
        <p v-else class="page-subtitle">Gestiona los dispositivos del inventario</p>
        <div class="states-info">
          <span class="states-label">Estados posibles:</span>
          <DeviceStatusBadge status="disponible" />
          <DeviceStatusBadge status="prestado" />
          <DeviceStatusBadge status="en_mantenimiento" />
          <DeviceStatusBadge status="de_baja" />
        </div>
      </div>
      <Button icon="pi pi-plus" label="Nuevo Dispositivo" @click="openCreateDrawer" />
    </div>

    <!-- Tabla -->
    <Card>
      <template #content>
        <DataTable :value="filteredDevices" :loading="loading" dataKey="id" stripedRows>
          <template #empty>
            <div class="text-center py-6 text-muted-color">No hay dispositivos registrados.</div>
          </template>

          <Column header="Producto">
            <template #body="{ data }">{{ data.product?.name ?? '—' }}</template>
          </Column>

          <Column field="internalCode" header="Código interno">
            <template #body="{ data }">{{ data.internalCode ?? '—' }}</template>
          </Column>

          <Column field="serialNumber" header="N° Serie">
            <template #body="{ data }">{{ data.serialNumber ?? '—' }}</template>
          </Column>

          <Column header="Estado" style="width: 140px">
            <template #body="{ data }">
              <DeviceStatusBadge :status="data.status?.name ?? ''" />
            </template>
          </Column>

          <Column header="Ubicación">
            <template #body="{ data }">{{ data.ubication?.name ?? '—' }}</template>
          </Column>

          <Column field="createdAt" header="Registrado" style="width: 120px">
            <template #body="{ data }">
              {{ new Date(data.createdAt).toLocaleDateString('es-CL') }}
            </template>
          </Column>

          <Column header="Acciones" style="width: 100px">
            <template #body="{ data }">
              <Button
                icon="pi pi-pencil"
                rounded
                text
                severity="secondary"
                v-tooltip.top="'Editar'"
                @click="openEditDrawer(data)"
              />
              <Button
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

    <!-- Drawer -->
    <Drawer
      v-model:visible="showDrawer"
      :header="drawerMode === 'create' ? 'Nuevo dispositivo' : 'Editar dispositivo'"
      position="right"
      style="width: 440px"
      :dismissable="!submitting"
    >
      <div v-if="drawerLoading" class="py-12 text-center text-muted-color">
        <i class="pi pi-spin pi-spinner text-2xl" />
        <p class="mt-2">Cargando...</p>
      </div>

      <!-- Producto con formulario -->
      <DeviceForm
        v-else
        :initial-values="drawerInitialValues"
        :products="products"
        :statuses="statuses"
        :ubications="ubications"
        :submitting="submitting"
        @submit="handleSubmit"
        @cancel="showDrawer = false"
      />
    </Drawer>

    <!-- Dialog eliminación -->
    <Dialog
      v-model:visible="showDeleteDialog"
      header="Confirmar eliminación"
      modal
      :style="{ width: '380px' }"
    >
      <p>
        ¿Eliminar el dispositivo
        <strong>{{ deviceToDelete?.internalCode ?? `#${deviceToDelete?.id}` }}</strong
        >?
      </p>
      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="showDeleteDialog = false" />
        <Button label="Eliminar" severity="danger" icon="pi pi-trash" @click="handleDelete" />
      </template>
    </Dialog>
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
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.states-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
  flex-wrap: wrap;
}
.states-label {
  font-size: 0.8rem;
  color: var(--p-text-muted-color);
}
</style>
