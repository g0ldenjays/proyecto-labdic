<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { Device } from '@/types/device.types'
import type { Category } from '@/types/catalog.types'
import { getAvailableDevices } from '@/services/device.service'
import { getCategories } from '@/services/catalog.service'
import { createLoan, getLoans, getMyLoans } from '@/services/loan.service'
import DeviceStatusBadge from '@/components/ui/DevicesStatusBadge.vue'
import { useUserStore } from '@/stores/user.store'
import type { User } from '@/types/user.types'
import { getUsers } from '@/services/user.service'
import { getBooks } from '@/services/book.service'
import type { Book } from '@/types/book.types'

const router = useRouter()
const toast = useToast()
const userStore = useUserStore()

// ── Datos ─────────────────────────────────────────────────────────────
const activeCatalogTab = ref<'devices' | 'books'>('devices')

const loading = ref(false)
const devices = ref<Device[]>([])
const categories = ref<Category[]>([])
const users = ref<User[]>([])
const selectedRequesterId = ref<number | null>(null)
const books = ref<Book[]>([])
const selectedBookIds = ref<number[]>([])
const bookSearch = ref('')
const filterTopic = ref<string | null>(null)

async function loadData() {
  loading.value = true

  try {
    devices.value = await getAvailableDevices()
  } catch {
    devices.value = []
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron cargar los dispositivos.',
      life: 4000,
    })
  }

  try {
    categories.value = await getCategories()
  } catch {
    categories.value = []
  }

  try {
    books.value = await getBooks()
  } catch {
    books.value = []
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron cargar los libros.',
      life: 4000,
    })
  }

  try {
    users.value = userStore.isAdmin ? await getUsers() : []

    if (userStore.isAdmin && !selectedRequesterId.value) {
      selectedRequesterId.value = userStore.currentUser?.id ?? null
    }
  } catch {
    users.value = []
  } finally {
    loading.value = false
  }
}

// ── Filtros ───────────────────────────────────────────────────────────
const filterCategory = ref<number | null>(null)
const filterSearch = ref('')

const categoryFilterOptions = computed(() =>
  categories.value.map((category) => ({
    ...category,
    count: devices.value.filter((device) => device.product?.categoryId === category.id).length,
  })),
)

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

const bookTopicOptions = computed(() => {
  const map = new Map<string, { label: string; value: string; count: number }>()

  books.value.forEach(book => {
    if (!book.topic) return

    const existing = map.get(book.topic)

    if (existing) {
      existing.count += book.availableQuantity
    } else {
      map.set(book.topic, {
        label: book.topic,
        value: book.topic,
        count: book.availableQuantity,
      })
    }
  })

  return Array.from(map.values()).sort((a, b) => a.label.localeCompare(b.label))
})

const filteredBooks = computed(() => {
  const query = bookSearch.value.trim().toLowerCase()

  return books.value.filter(book => {
    const matchesSearch =
      !query ||
      book.title.toLowerCase().includes(query) ||
      book.author?.toLowerCase().includes(query) ||
      book.isbn?.toLowerCase().includes(query)

    const matchesTopic =
      !filterTopic.value || book.topic === filterTopic.value

    return matchesSearch && matchesTopic && book.availableQuantity > 0
  })
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
const additionalItems = ref('')

function openCartDrawer() {
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

function isBookSelected(bookId: number) {
  return selectedBookIds.value.includes(bookId)
}

function toggleBookSelection(bookId: number) {
  if (isBookSelected(bookId)) {
    selectedBookIds.value = selectedBookIds.value.filter(id => id !== bookId)
    return
  }

  selectedBookIds.value = [...selectedBookIds.value, bookId]
}

const selectedBooks = computed(() =>
  books.value.filter(book => selectedBookIds.value.includes(book.id)),
)

// ── Dialog solicitud de préstamo ─────────────────────────────────────
const showLoanDialog = ref(false)
const loanReason = ref('')
const loanEstimatedReturn = ref<Date | null>(null)
const submittingLoan = ref(false)

async function openLoanDialog() {
  if (selectedDeviceIds.value.length === 0 && selectedBookIds.value.length === 0 && !additionalItems.value.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Carrito vacío',
      detail: 'Agrega al menos un dispositivo o un elemento adicional al carrito.',
      life: 3000,
    })
    return
  }

  loanReason.value = ''
  loanEstimatedReturn.value = null

  if (userStore.isAdmin) {
    selectedRequesterId.value = userStore.currentUser?.id ?? null
  }

  showLoanDialog.value = true
}

async function validateNoDuplicateActiveLoans() {
  const requesterId = userStore.isAdmin ? selectedRequesterId.value : userStore.currentUser?.id

  if (!requesterId) return true

  try {
    const loans = userStore.isAdmin ? await getLoans() : await getMyLoans()

    const activeDeviceIds = loans
      .filter((loan) => loan.userId === requesterId || !userStore.isAdmin)
      .filter((loan) => ['pendiente', 'aprobado', 'prestado'].includes(loan.status?.name ?? ''))
      .flatMap((loan) => loan.loanRequestItems?.map((item) => item.deviceId) ?? [])

    const duplicates = selectedDeviceIds.value.filter((id) => activeDeviceIds.includes(id))

    if (duplicates.length > 0) {
      const names = selectedDevices.value
        .filter((device) => duplicates.includes(device.id))
        .map((device) => device.product?.name ?? `#${device.id}`)
        .join(', ')

      toast.add({
        severity: 'warn',
        summary: 'Solicitud duplicada',
        detail: `El solicitante ya tiene una solicitud activa para: ${names}.`,
        life: 5000,
      })

      return false
    }

    return true
  } catch {
    return true
  }
}

async function handleCreateLoan() {
  if (userStore.isAdmin && !selectedRequesterId.value) {
    toast.add({
      severity: 'warn',
      summary: 'Solicitante requerido',
      detail: 'Debes seleccionar para quién se realizará la solicitud.',
      life: 3000,
    })
    return
  }

  const canContinue = await validateNoDuplicateActiveLoans()
  if (!canContinue) return

  submittingLoan.value = true
  try {
    await createLoan({
      deviceIds: selectedDeviceIds.value,
      bookIds: selectedBookIds.value,
      reason: loanReason.value || undefined,
      estimatedReturnDate: loanEstimatedReturn.value
        ? loanEstimatedReturn.value.toISOString()
        : undefined,
      requestedUserId: userStore.isAdmin ? (selectedRequesterId.value ?? undefined) : undefined,
      additionalItems: additionalItems.value.trim() || undefined,
    })

    toast.add({
      severity: 'success',
      summary: 'Solicitud enviada',
      detail: userStore.isAdmin
        ? 'La solicitud fue registrada correctamente para el usuario seleccionado.'
        : 'Tu solicitud fue enviada correctamente. Puedes revisarla en "Mis Solicitudes".',
      life: 5000,
    })

    showLoanDialog.value = false
    selectedDeviceIds.value = []
    selectedBookIds.value = []
    additionalItems.value = ''

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
          :label="`Ver carrito (${selectedDeviceIds.length + selectedBookIds.length})`"
          icon="pi pi-shopping-cart"
          @click="openCartDrawer"
        />
      </Transition>
    </div>

    <div class="catalog-tabs">
      <Button
        label="Dispositivos"
        :severity="activeCatalogTab === 'devices' ? 'primary' : 'secondary'"
        :outlined="activeCatalogTab !== 'devices'"
        @click="activeCatalogTab = 'devices'"
      />

      <Button
        label="Libros"
        :severity="activeCatalogTab === 'books' ? 'primary' : 'secondary'"
        :outlined="activeCatalogTab !== 'books'"
        @click="activeCatalogTab = 'books'"
      />
    </div>

    <template v-if="activeCatalogTab === 'devices'">
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
              :options="categoryFilterOptions"
              optionLabel="name"
              optionValue="id"
              placeholder="Todas las categorías"
              showClear
              class="filter-category"
            >
              <template #option="{ option }">
                <div class="filter-option">
                  <span>{{ option.name }}</span>
                  <span class="filter-option-count">{{ option.count }}</span>
                </div>
              </template>
            </Select>
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
          · {{ selectedDeviceIds.length }} seleccionado{{
            selectedDeviceIds.length !== 1 ? 's' : ''
          }}
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

            <Column header="Observación">
              <template #body="{ data }">
                <span class="observation-text">
                  {{ data.observation ?? '—' }}
                </span>
              </template>
            </Column>

            <Column header="" style="width: 180px">
              <template #body="{ data }">
                <div class="action-cell">
                  <Button
                    :label="isSelected(data.id) ? 'Quitar' : 'Agregar'"
                    :severity="isSelected(data.id) ? 'danger' : 'primary'"
                    outlined
                    size="small"
                    :icon="isSelected(data.id) ? 'pi pi-cart-minus' : 'pi pi-cart-arrow-down'"
                    @click="toggleSelection(data.id)"
                  />
                </div>
              </template>
            </Column>
          </DataTable>

          <div class="cart-bottom-action">
            <Button
              :label="`Ver carrito (${selectedDeviceIds.length})`"
              icon="pi pi-shopping-cart"
              @click="openCartDrawer"
            />
          </div>
        </template>
      </Card>
    </template>

    <template v-else>
      <div class="filters-card">
        <div class="filters-row">
          <span class="p-input-icon-left catalog-search">
            <i class="pi pi-search" />
            <InputText v-model="bookSearch" placeholder="Buscar por título, autor o ISBN" />
          </span>

          <Select
            v-model="filterTopic"
            :options="bookTopicOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Filtrar por temática"
            showClear
          >
            <template #option="{ option }">
              <div class="filter-option">
                <span>{{ option.label }}</span>
                <span class="filter-option-count">{{ option.count }}</span>
              </div>
            </template>
          </Select>
        </div>
      </div>

      <DataTable
        :value="filteredBooks"
        dataKey="id"
        responsiveLayout="scroll"
        class="catalog-table"
      >
        <Column field="title" header="Libro" sortable />

        <Column field="author" header="Autor">
          <template #body="{ data }">
            {{ data.author ?? '—' }}
          </template>
        </Column>

        <Column field="topic" header="Temática">
          <template #body="{ data }">
            {{ data.topic ?? '—' }}
          </template>
        </Column>

        <Column field="isbn" header="ISBN">
          <template #body="{ data }">
            {{ data.isbn ?? '—' }}
          </template>
        </Column>

        <Column field="availableQuantity" header="Disponibles" sortable />

        <Column header="" style="width: 150px">
          <template #body="{ data }">
            <Button
              :label="isBookSelected(data.id) ? 'Quitar' : 'Agregar'"
              :severity="isBookSelected(data.id) ? 'danger' : 'primary'"
              outlined
              :icon="isBookSelected(data.id) ? 'pi pi-cart-minus' : 'pi pi-cart-arrow-down'"
              size="small"
              @click="toggleBookSelection(data.id)"
            />
          </template>
        </Column>
      </DataTable>
    </template>

    <!-- Drawer carrito -->
    <Drawer v-model:visible="showCartDrawer" header="Carrito" position="right" style="width: 440px">
      <div class="cart-drawer-content">
        <p class="cart-intro">Estás a punto de solicitar los siguientes elementos:</p>

        <div v-if="selectedDevices.length === 0" class="cart-empty">
          No hay dispositivos en el carrito.
        </div>

        <div v-else class="cart-device-list">
          <h3 class="cart-section-title">Dispositivos</h3>
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

        <div v-if="selectedBooks.length > 0" class="cart-device-list">
          <h3 class="cart-section-title">Libros</h3>

          <div v-for="book in selectedBooks" :key="book.id" class="cart-device-item">
            <div class="cart-device-info">
              <span class="cart-device-name">
                {{ book.title }}
              </span>
              <span class="cart-device-detail">
                {{ book.author ?? 'Autor no registrado' }}
              </span>
              <span class="cart-device-detail"> Temática: {{ book.topic ?? '—' }} </span>
            </div>

            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              v-tooltip.left="'Quitar del carrito'"
              @click="toggleBookSelection(book.id)"
            />
          </div>
        </div>

        <div class="cart-section">
          <h3 class="cart-section-title">Elementos adicionales</h3>

          <p class="cart-help-text">Escribe aquí elementos sin código de inventario.</p>

          <Textarea
            v-model="additionalItems"
            rows="4"
            autoResize
            placeholder="Describe los elementos adicionales que necesitas..."
          />
        </div>

        <div class="cart-drawer-actions">
          <Button label="Seguir viendo" severity="secondary" text @click="continueWatching" />

          <Button
            label="Continuar solicitud"
            icon="pi pi-send"
            :disabled="
              selectedDevices.length === 0 && selectedBooks.length === 0 && !additionalItems.trim()
            "
            @click="startLoanRequestFromCart"
          />
        </div>
      </div>
    </Drawer>

    <!-- Dialog solicitud -->
    <Dialog
      v-model:visible="showLoanDialog"
      header="Solicitar elementos"
      modal
      :style="{ width: '480px' }"
      :closable="!submittingLoan"
    >
      <div class="loan-dialog-content">
        <div class="selected-devices-section">
          <label class="section-label">Elementos inventariados</label>
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

        <div v-if="selectedBooks.length > 0" class="selected-devices-section">
          <label class="section-label">Libros</label>

          <div class="selected-devices-list">
            <div v-for="book in selectedBooks" :key="book.id" class="selected-device-item">
              <i class="pi pi-book text-muted-color" />
              <span>{{ book.title }}</span>
              <span class="device-code text-muted-color">
                {{ book.author ?? '—' }}
              </span>
            </div>
          </div>
        </div>

        <div v-if="additionalItems.trim()" class="selected-devices-section">
          <label class="section-label">Elementos adicionales</label>
          <div class="additional-items-preview">
            {{ additionalItems }}
          </div>
        </div>

        <div v-if="userStore.isAdmin" class="flex flex-col gap-1">
          <label class="font-medium">Solicitante</label>
          <Select
            v-model="selectedRequesterId"
            :options="users"
            optionLabel="name"
            optionValue="id"
            placeholder="Selecciona el solicitante"
            filter
            :disabled="submittingLoan"
          />
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
          label="Enviar solicitud"
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
.filter-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  width: 100%;
}
.filter-option-count {
  min-width: 2.25rem;
  padding: 0.25rem 0.55rem;
  border-radius: 0.65rem;
  text-align: center;
  font-size: 0.85rem;
  font-weight: 600;
  background: var(--p-surface-200, #e5e7eb);
  color: var(--p-text-color);
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
.observation-text {
  display: block;
  max-width: 260px;
  line-height: 1.35;
  color: var(--p-text-color);
  white-space: normal;
  word-break: break-word;
}
.action-cell {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
.observation-text {
  line-height: 1.35;
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

.cart-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cart-section-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
}

.cart-help-text {
  margin: 0;
  font-size: 0.8rem;
  color: var(--p-text-muted-color);
}

.additional-items-preview {
  padding: 0.75rem;
  border-radius: 8px;
  background: var(--p-surface-50, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--p-surface-100, rgba(0, 0, 0, 0.05));
  white-space: pre-wrap;
  font-size: 0.875rem;
}

.catalog-tabs {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
</style>
