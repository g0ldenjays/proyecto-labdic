<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { Device } from '@/types/device.types'
import type { Category } from '@/types/catalog.types'
import { getAvailableDevices } from '@/services/device.service'
import { getCategories } from '@/services/catalog.service'
import { createLoan, getMyLoans } from '@/services/loan.service'
import DeviceStatusBadge from '@/components/ui/DevicesStatusBadge.vue'

const router = useRouter()
const toast = useToast()

// ── Datos ─────────────────────────────────────────────────────────────
const loading = ref(false)
const devices = ref<Device[]>([])
const categories = ref<Category[]>([])

async function loadData() {
  loading.value = true
  try {
    const [d, c] = await Promise.all([getAvailableDevices(), getCategories()])
    devices.value = d
    categories.value = c
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el catálogo.',
      life: 4000,
    })
  } finally {
    loading.value = false
  }
}

// ── Filtros ───────────────────────────────────────────────────────────
const filterCategory = ref<number | null>(null)
const filterSearch = ref('')

const filteredDevices = computed(() => {
  let result = devices.value
  if (filterCategory.value) {
    result = result.filter((d) => d.product?.categoryId === filterCategory.value)
  }
  if (filterSearch.value.trim()) {
    const q = filterSearch.value.toLowerCase()
    result = result.filter(
      (d) =>
        d.product?.name?.toLowerCase().includes(q) ||
        d.internalCode?.toLowerCase().includes(q) ||
        d.serialNumber?.toLowerCase().includes(q),
    )
  }
  return result
})

function clearFilters() {
  filterCategory.value = null
  filterSearch.value = ''
}

// ── Selección ─────────────────────────────────────────────────────────
const selectedDeviceIds = ref<number[]>([])

function toggleSelection(deviceId: number) {
  const idx = selectedDeviceIds.value.indexOf(deviceId)
  if (idx === -1) selectedDeviceIds.value.push(deviceId)
  else selectedDeviceIds.value.splice(idx, 1)
}

function isSelected(deviceId: number) {
  return selectedDeviceIds.value.includes(deviceId)
}

const selectedDevices = computed(() =>
  devices.value.filter((d) => selectedDeviceIds.value.includes(d.id)),
)

const showCartDrawer = ref(false)

function openCartDrawer() {
  if (selectedDeviceIds.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: 'Carrito vacío',
      detail: 'Agrega al menos un dispositivo al carrito.',
      life: 3000,
    })
    return
  }

  showCartDrawer.value = true
}

function removeFromCart(deviceId: number) {
  selectedDeviceIds.value = selectedDeviceIds.value.filter((id) => id !== deviceId)

  if (selectedDeviceIds.value.length === 0) {
    showCartDrawer.value = false
  }
}

function continueWatching() {
  showCartDrawer.value = false
}

async function startLoanRequestFromCart() {
  showCartDrawer.value = false
  await openLoanDialog()
}

// ── Dialog solicitud de préstamo ─────────────────────────────────────
const showLoanDialog = ref(false)
const loanReason = ref('')
const loanEstimatedReturn = ref<Date | null>(null)
const submittingLoan = ref(false)

async function openLoanDialog() {
  if (selectedDeviceIds.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: 'Sin selección',
      detail: 'Selecciona al menos un dispositivo.',
      life: 3000,
    })
    return
  }

  // Verificar solicitudes activas del usuario para evitar duplicados
  try {
    const myLoans = await getMyLoans()
    const activeDeviceIds = myLoans
      .filter((l) => ['pendiente', 'aprobado', 'prestado'].includes(l.status?.name ?? ''))
      .flatMap((l) => l.loanRequestItems?.map((item) => item.deviceId) ?? [])

    const duplicates = selectedDeviceIds.value.filter((id) => activeDeviceIds.includes(id))

    if (duplicates.length > 0) {
      const names = selectedDevices.value
        .filter((d) => duplicates.includes(d.id))
        .map((d) => d.product?.name ?? `#${d.id}`)
        .join(', ')
      toast.add({
        severity: 'warn',
        summary: 'Solicitud duplicada',
        detail: `Ya tienes una solicitud activa para: ${names}.`,
        life: 5000,
      })
      return
    }
  } catch {
    // Si falla la verificación, dejamos continuar igual
  }

  loanReason.value = ''
  loanEstimatedReturn.value = null
  showLoanDialog.value = true
}

async function handleCreateLoan() {
  submittingLoan.value = true
  try {
    await createLoan({
      deviceIds: selectedDeviceIds.value,
      reason: loanReason.value || undefined,
      estimatedReturnDate: loanEstimatedReturn.value
        ? loanEstimatedReturn.value.toISOString()
        : undefined,
    })

    toast.add({
      severity: 'success',
      summary: 'Solicitud enviada',
      detail: 'Tu solicitud fue enviada correctamente. Puedes revisarla en "Mis Solicitudes".',
      life: 5000,
    })

    showLoanDialog.value = false
    selectedDeviceIds.value = []

    // Recargar catálogo para reflejar cambios de disponibilidad
    await loadData()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo enviar la solicitud. Intenta nuevamente.',
      life: 4000,
    })
  } finally {
    submittingLoan.value = false
  }
}

function getRowClass(device: Device) {
  return isSelected(device.id) ? 'cart-row' : ''
}

onMounted(loadData)
</script>

<template>
  <div class="page-container">
    <!-- Cabecera -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Catálogo de Dispositivos</h1>
        <p class="page-subtitle">Selecciona los dispositivos que deseas solicitar en préstamo</p>
      </div>
      <Transition name="fade">
        <Button
          v-if="selectedDeviceIds.length > 0"
          :label="`Solicitar carrito (${selectedDeviceIds.length})`"
          icon="pi pi-shopping-cart"
          @click="openCartDrawer"
        />
      </Transition>
    </div>

    <!-- Filtros -->
    <Card>
      <template #content>
        <div class="filters-row">
          <InputText
            v-model="filterSearch"
            placeholder="Buscar por nombre, código o serie..."
            class="filter-search"
          />
          <Select
            v-model="filterCategory"
            :options="categories"
            optionLabel="name"
            optionValue="id"
            placeholder="Todas las categorías"
            showClear
            class="filter-category"
          />
          <Button
            v-if="filterCategory || filterSearch"
            label="Limpiar"
            severity="secondary"
            text
            icon="pi pi-times"
            @click="clearFilters"
          />
        </div>
      </template>
    </Card>

    <!-- Contador -->
    <div class="results-info">
      <span
        >{{ filteredDevices.length }} dispositivo{{
          filteredDevices.length !== 1 ? 's' : ''
        }}
        disponible{{ filteredDevices.length !== 1 ? 's' : '' }}</span
      >
      <span v-if="selectedDeviceIds.length > 0" class="selected-count">
        · {{ selectedDeviceIds.length }} seleccionado{{ selectedDeviceIds.length !== 1 ? 's' : '' }}
      </span>
    </div>

    <!-- Tabla -->
    <Card>
      <template #content>
        <DataTable
          :value="filteredDevices"
          :loading="loading"
          dataKey="id"
          stripedRows
          :rowClass="getRowClass"
        >
          <template #empty>
            <div class="text-center py-8 text-muted-color">
              <i class="pi pi-inbox text-4xl block mb-3 opacity-30" />
              No hay dispositivos disponibles en este momento.
            </div>
          </template>

          <Column style="width: 52px">
            <template #body="{ data }">
              <Checkbox
                :modelValue="isSelected(data.id)"
                :binary="true"
                @change="toggleSelection(data.id)"
              />
            </template>
          </Column>

          <Column header="Dispositivo">
            <template #body="{ data }">
              <div class="product-info">
                <span class="product-name">{{ data.product?.name ?? '—' }}</span>
                <span v-if="data.product?.category" class="product-category">{{
                  data.product.category.name
                }}</span>
              </div>
            </template>
          </Column>

          <Column field="internalCode" header="Código">
            <template #body="{ data }">{{ data.internalCode ?? '—' }}</template>
          </Column>

          <Column header="Estado" style="width: 130px">
            <template #body="{ data }">
              <DeviceStatusBadge :status="data.status?.name ?? ''" />
            </template>
          </Column>

          <Column header="Ubicación">
            <template #body="{ data }">{{ data.ubication?.name ?? '—' }}</template>
          </Column>

          <Column style="width: 130px">
            <template #body="{ data }">
              <Button
                :label="isSelected(data.id) ? 'Quitar' : 'Agregar al carrito'"
                :severity="isSelected(data.id) ? 'secondary' : 'primary'"
                :outlined="!isSelected(data.id)"
                size="small"
                @click="toggleSelection(data.id)"
              />
            </template>
          </Column>
        </DataTable>

        <div v-if="selectedDeviceIds.length > 0" class="cart-bottom-action">
          <Button
            :label="`Solicitar carrito (${selectedDeviceIds.length})`"
            icon="pi pi-shopping-cart"
            @click="openCartDrawer"
          />
        </div>
      </template>
    </Card>

    <!-- Drawer carrito -->
    <Drawer v-model:visible="showCartDrawer" header="Carrito" position="right" style="width: 440px">
      <div class="cart-drawer-content">
        <p class="cart-intro">Estás a punto de solicitar los siguientes dispositivos:</p>

        <div v-if="selectedDevices.length === 0" class="cart-empty">
          No hay dispositivos en el carrito.
        </div>

        <div v-else class="cart-device-list">
          <div v-for="device in selectedDevices" :key="device.id" class="cart-device-item">
            <div class="cart-device-info">
              <span class="cart-device-name">
                {{ device.product?.name ?? '—' }}
              </span>
              <span class="cart-device-detail">
                {{ device.internalCode ?? `#${device.id}` }}
              </span>
              <span v-if="device.serialNumber" class="cart-device-detail">
                Serie: {{ device.serialNumber }}
              </span>
            </div>

            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              v-tooltip.left="'Quitar del carrito'"
              @click="removeFromCart(device.id)"
            />
          </div>
        </div>

        <div class="cart-drawer-actions">
          <Button label="Seguir viendo" severity="secondary" text @click="continueWatching" />

          <Button
            label="Solicitar dispositivos"
            icon="pi pi-send"
            :disabled="selectedDevices.length === 0"
            @click="startLoanRequestFromCart"
          />
        </div>
      </div>
    </Drawer>

    <!-- Dialog solicitud -->
    <Dialog
      v-model:visible="showLoanDialog"
      header="Solicitar dispositivos"
      modal
      :style="{ width: '480px' }"
      :closable="!submittingLoan"
    >
      <div class="loan-dialog-content">
        <div class="selected-devices-section">
          <label class="section-label">Dispositivos seleccionados</label>
          <div class="selected-devices-list">
            <div v-for="device in selectedDevices" :key="device.id" class="selected-device-item">
              <i class="pi pi-server text-muted-color" />
              <span>{{ device.product?.name ?? '—' }}</span>
              <span class="device-code text-muted-color">{{
                device.internalCode ?? `#${device.id}`
              }}</span>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-medium">Motivo del préstamo</label>
          <Textarea
            v-model="loanReason"
            rows="3"
            placeholder="Describe brevemente para qué necesitas el dispositivo..."
            :disabled="submittingLoan"
          />
        </div>

        <div class="flex flex-col gap-1">
          <label class="font-medium">Fecha estimada de devolución</label>
          <DatePicker
            v-model="loanEstimatedReturn"
            :minDate="new Date()"
            dateFormat="dd/mm/yy"
            placeholder="Selecciona una fecha"
            showIcon
            :disabled="submittingLoan"
          />
        </div>
      </div>

      <template #footer>
        <Button
          label="Cancelar"
          severity="secondary"
          text
          :disabled="submittingLoan"
          @click="showLoanDialog = false"
        />
        <Button
          label="Solicitar dispositivos"
          icon="pi pi-send"
          :loading="submittingLoan"
          @click="handleCreateLoan"
        />
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
}
.filters-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.filter-search {
  flex: 1;
  min-width: 200px;
}
.filter-category {
  width: 200px;
}
.results-info {
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
}
.selected-count {
  color: var(--p-primary-color);
  font-weight: 600;
}
.product-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.product-name {
  font-weight: 500;
  font-size: 0.9rem;
}
.product-category {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
}
.loan-dialog-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.section-label {
  font-weight: 600;
  font-size: 0.875rem;
  display: block;
  margin-bottom: 0.5rem;
}
.selected-devices-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  max-height: 150px;
  overflow-y: auto;
}
.selected-device-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  background: var(--p-surface-50, rgba(0, 0, 0, 0.03));
  font-size: 0.875rem;
}
.device-code {
  margin-left: auto;
  font-size: 0.8rem;
}
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 200ms,
    transform 200ms;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
:deep(.cart-row) {
  background: rgba(34, 197, 94, 0.12) !important;
}
:deep(.cart-row:hover) {
  background: rgba(34, 197, 94, 0.18) !important;
}
.cart-bottom-action {
  display: flex;
  justify-content: flex-end;
  padding-top: 1rem;
  margin-top: 1rem;
  border-top: 1px solid var(--p-surface-200, rgba(0, 0, 0, 0.08));
}
.cart-drawer-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}
.cart-intro {
  margin: 0;
  color: var(--p-text-muted-color);
  font-size: 0.9rem;
}
.cart-empty {
  padding: 1rem;
  text-align: center;
  color: var(--p-text-muted-color);
  border: 1px dashed var(--p-surface-300, rgba(0, 0, 0, 0.15));
  border-radius: 8px;
}
.cart-device-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  overflow-y: auto;
  padding-right: 0.25rem;
}
.cart-device-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 1px solid var(--p-surface-200, rgba(0, 0, 0, 0.08));
  border-radius: 8px;
  background: var(--p-surface-0, #ffffff);
}
.cart-device-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}
.cart-device-name {
  font-weight: 600;
  font-size: 0.9rem;
}
.cart-device-detail {
  color: var(--p-text-muted-color);
  font-size: 0.8rem;
}
.cart-drawer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--p-surface-200, rgba(0, 0, 0, 0.08));
}
</style>
