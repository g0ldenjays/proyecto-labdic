<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import DeviceStatusBadge from '@/components/ui/DevicesStatusBadge.vue'
import InventoryTransferDrawer from '@/modules/inventory-admin/components/InventoryTransferDrawer.vue'
import InventoryWriteoffDrawer from '@/modules/inventory-admin/components/InventoryWriteoffDrawer.vue'
import type { Category, Status, Ubication } from '@/types/catalog.types'
import type { Device } from '@/types/device.types'
import { getCategories, getStatuses, getUbications } from '@/services/catalog.service'

import type {
  InventoryAdminFilters,
  InventoryAlerts,
  InventoryDashboard,
  InventoryTransferPayload,
  InventoryWriteoffPayload,
} from '@/types/inventory-admin.types'

import {
  getInventoryDashboard,
  getInventoryDevices,
  getInventoryAlerts,
  downloadInventoryXlsx,
  createInventoryTransfer,
  downloadTransferPdf,
  createInventoryWriteoff,
  downloadWriteoffPdf,
} from '@/services/inventory-admin.service'

const toast = useToast()

const loadingDashboard = ref(false)
const loadingInventory = ref(false)
const exportingXlsx = ref(false)

const dashboard = ref<InventoryDashboard | null>(null)
const devices = ref<Device[]>([])
const selectedDevices = ref<Device[]>([])
const openSections = ref([])

const statuses = ref<Status[]>([])
const ubications = ref<Ubication[]>([])
const categories = ref<Category[]>([])

const filters = ref<InventoryAdminFilters>({
  search: '',
  statusId: null,
  ubicationId: null,
  categoryId: null,
})

const showTransferDrawer = ref(false)
const transferring = ref(false)

const showWriteoffDrawer = ref(false)
const writingOff = ref(false)

const loadingAlerts = ref(false)
const alerts = ref<InventoryAlerts | null>(null)

function clearSelection() {
  selectedDevices.value = []
}

async function loadCatalogs() {
  try {
    const [statusesData, ubicationsData, categoriesData] = await Promise.all([
      getStatuses(),
      getUbications(),
      getCategories(),
    ])
    statuses.value = statusesData
    ubications.value = ubicationsData
    categories.value = categoriesData
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron cargar los filtros del inventario.',
      life: 4000,
    })
  }
}

async function loadDashboard() {
  loadingDashboard.value = true
  try {
    dashboard.value = await getInventoryDashboard()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el dashboard administrativo.',
      life: 4000,
    })
  } finally {
    loadingDashboard.value = false
  }
}

async function loadInventory() {
  loadingInventory.value = true
  try {
    devices.value = await getInventoryDevices(filters.value)

    const visibleIds = new Set(devices.value.map(device => device.id))
    selectedDevices.value = selectedDevices.value.filter(device => visibleIds.has(device.id))
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el listado administrativo.',
      life: 4000,
    })
  } finally {
    loadingInventory.value = false
  }
}

async function refreshAll() {
  await Promise.all([loadDashboard(), loadInventory(), loadAlerts()])
}

function clearFilters() {
  filters.value = {
    search: '',
    statusId: null,
    ubicationId: null,
    categoryId: null,
  }
  clearSelection()
  loadInventory()
}

async function handleExportXlsx() {
  exportingXlsx.value = true
  try {
    await downloadInventoryXlsx(filters.value)
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo exportar el inventario en XLSX.',
      life: 4000,
    })
  } finally {
    exportingXlsx.value = false
  }
}

function openTransferDrawer() {
  showTransferDrawer.value = true
}

function closeTransferDrawer() {
  showTransferDrawer.value = false
}

async function handleTransfer(payload: Omit<InventoryTransferPayload, 'deviceIds'>) {
  if (selectedDevices.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: 'Sin selección',
      detail: 'Debes seleccionar al menos un dispositivo.',
      life: 3000,
    })
    return
  }

  if (!payload.targetUbicationName?.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Campo requerido',
      detail: 'Debes ingresar una ubicación destino.',
      life: 3000,
    })
    return
  }

  transferring.value = true
  try {
    const result = await createInventoryTransfer({
      deviceIds: selectedDevices.value.map(device => device.id),
      targetUbicationName: payload.targetUbicationName.trim(),
      reason: payload.reason || null,
      observations: payload.observations || null,
    })

    toast.add({
      severity: 'success',
      summary: 'Traslado realizado',
      detail: `Se trasladaron ${result.updatedDevices} dispositivo(s).`,
      life: 4000,
    })

    closeTransferDrawer()
    clearSelection()

    await loadCatalogs()
    await refreshAll()

    // si falla el PDF, no debe marcar como fallo del traslado
    try {
      await downloadTransferPdf(result.documentId)
    } catch {
      toast.add({
        severity: 'warn',
        summary: 'PDF no disponible',
        detail: 'El traslado se registró correctamente, pero no se pudo descargar el PDF.',
        life: 5000,
      })
    }
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo registrar el traslado.',
      life: 4000,
    })
  } finally {
    transferring.value = false
  }
}

function openWriteoffDrawer() {
  showWriteoffDrawer.value = true
}

function closeWriteoffDrawer() {
  showWriteoffDrawer.value = false
}

async function handleWriteoff(payload: Omit<InventoryWriteoffPayload, 'deviceIds'>) {
  if (selectedDevices.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: 'Sin selección',
      detail: 'Debes seleccionar al menos un dispositivo.',
      life: 3000,
    })
    return
  }

  writingOff.value = true
  try {
    const result = await createInventoryWriteoff({
      deviceIds: selectedDevices.value.map(device => device.id),
      reason: payload.reason || null,
      observations: payload.observations || null,
    })

    toast.add({
      severity: 'success',
      summary: 'Baja registrada',
      detail: `Se dieron de baja ${result.updatedDevices} dispositivo(s).`,
      life: 4000,
    })

    closeWriteoffDrawer()
    clearSelection()
    await refreshAll()

    try {
      await downloadWriteoffPdf(result.documentId)
    } catch {
      toast.add({
        severity: 'warn',
        summary: 'PDF no disponible',
        detail: 'La baja se registró correctamente, pero no se pudo descargar el PDF.',
        life: 5000,
      })
    }
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo registrar la baja.',
      life: 4000,
    })
  } finally {
    writingOff.value = false
  }
}

async function loadAlerts() {
  loadingAlerts.value = true
  try {
    alerts.value = await getInventoryAlerts()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron cargar las alertas del inventario.',
      life: 4000,
    })
  } finally {
    loadingAlerts.value = false
  }
}

onMounted(async () => {
  await loadCatalogs()
  await refreshAll()
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <h1 class="text-2xl font-bold">Administración de Inventario</h1>
        <p class="text-sm text-surface-500">
          Vista administrativa del inventario del LabDIC.
        </p>
      </div>

      <div class="flex items-center gap-3">

        <Button
          label="Recargar"
          icon="pi pi-refresh"
          severity="secondary"
          @click="refreshAll"
          :loading="loadingDashboard || loadingInventory || loadingAlerts"
        />

        <div class="inventory-kpi">
          <div class="inventory-kpi-icon">
            <i class="pi pi-server" />
          </div>

          <div class="inventory-kpi-content">
            <span class="inventory-kpi-label">Total dispositivos</span>
            <span class="inventory-kpi-value">
              {{ dashboard?.totalDevices ?? 0 }}
            </span>
          </div>
        </div>

      </div>
    </div>

    <Accordion v-model:value="openSections" multiple>
      <AccordionPanel value="grouped-view">
        <AccordionHeader>Vista agrupada</AccordionHeader>
        <AccordionContent>
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 pt-2">
            <Card>
              <template #title>Por estado</template>
              <template #content>
                <div v-if="loadingDashboard" class="text-surface-500">Cargando...</div>
                <div v-else class="flex flex-col gap-3">
                  <div
                    v-for="item in dashboard?.byStatus ?? []"
                    :key="item.label"
                    class="flex items-center justify-between"
                  >
                    <span>{{ item.label }}</span>
                    <Tag :value="String(item.count)" severity="secondary" />
                  </div>
                </div>
              </template>
            </Card>

            <Card>
              <template #title>Por ubicación</template>
              <template #content>
                <div v-if="loadingDashboard" class="text-surface-500">Cargando...</div>
                <div v-else class="flex flex-col gap-3">
                  <div
                    v-for="item in dashboard?.byUbication ?? []"
                    :key="item.label"
                    class="flex items-center justify-between"
                  >
                    <span>{{ item.label }}</span>
                    <Tag :value="String(item.count)" severity="secondary" />
                  </div>
                </div>
              </template>
            </Card>

            <Card>
              <template #title>Por categoría</template>
              <template #content>
                <div v-if="loadingDashboard" class="text-surface-500">Cargando...</div>
                <div v-else class="flex flex-col gap-3">
                  <div
                    v-for="item in dashboard?.byCategory ?? []"
                    :key="item.label"
                    class="flex items-center justify-between"
                  >
                    <span>{{ item.label }}</span>
                    <Tag :value="String(item.count)" severity="secondary" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </AccordionContent>
      </AccordionPanel>

      <AccordionPanel value="alerts">
        <AccordionHeader>Alertas</AccordionHeader>
        <AccordionContent>
          <div class="grid grid-cols-1 xl:grid-cols-2 gap-4 pt-2">
            <Card>
              <template #title>Mantención prolongada</template>
              <template #subtitle>
                {{ alerts?.maintenanceAlertDays ?? 0 }}+ días en mantención
              </template>

              <template #content>
                <div v-if="loadingAlerts" class="text-surface-500">Cargando alertas...</div>

                <div
                  v-else-if="!alerts?.prolongedMaintenance?.length"
                  class="text-sm text-surface-500"
                >
                  No hay dispositivos en mantención prolongada.
                </div>

                <div v-else class="flex flex-col gap-3">
                  <div
                    v-for="item in alerts?.prolongedMaintenance ?? []"
                    :key="item.deviceId"
                    class="border rounded p-3 flex flex-col gap-1"
                  >
                    <div class="font-medium">{{ item.productName }}</div>
                    <div class="text-sm text-surface-500">
                      {{ item.internalCode ?? 'Sin código' }} · {{ item.serialNumber ?? 'Sin serie' }}
                    </div>
                    <div class="text-sm text-surface-500">
                      Ubicación: {{ item.ubicationName ?? '—' }}
                    </div>
                    <Tag :value="`${item.daysInMaintenance} día(s)`" severity="warn" />
                  </div>
                </div>
              </template>
            </Card>

            <Card>
              <template #title>Préstamos vencidos</template>

              <template #content>
                <div v-if="loadingAlerts" class="text-surface-500">Cargando alertas...</div>

                <div
                  v-else-if="!alerts?.overdueLoans?.length"
                  class="text-sm text-surface-500"
                >
                  No hay préstamos vencidos.
                </div>

                <div v-else class="flex flex-col gap-3">
                  <div
                    v-for="loan in alerts?.overdueLoans ?? []"
                    :key="loan.loanId"
                    class="border rounded p-3 flex flex-col gap-2"
                  >
                    <div class="font-medium">
                      Solicitud #{{ loan.loanId }} · {{ loan.userName }}
                    </div>

                    <div class="text-sm text-surface-500">
                      @{{ loan.userUsername }}
                    </div>

                    <div class="text-sm text-surface-500">
                      Vencimiento: {{ new Date(loan.estimatedReturnDate).toLocaleDateString('es-CL') }}
                    </div>

                    <Tag :value="`${loan.daysOverdue} día(s) de atraso`" severity="danger" />

                    <div class="flex flex-col gap-1 mt-1">
                      <span class="text-sm font-medium">Dispositivos:</span>
                      <ul class="text-sm text-surface-600 pl-4 list-disc">
                        <li
                          v-for="device in loan.devices"
                          :key="device.deviceId"
                        >
                          {{ device.productName }} — {{ device.internalCode ?? 'Sin código' }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>

    <Card>
      <template #title>Inventario administrativo</template>
      <template #content>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText v-model="filters.search" placeholder="Buscar por producto, código o serie" />
          </IconField>

          <Select
            v-model="filters.statusId"
            :options="statuses"
            optionLabel="name"
            optionValue="id"
            placeholder="Estado"
            showClear
          />

          <Select
            v-model="filters.ubicationId"
            :options="ubications"
            optionLabel="name"
            optionValue="id"
            placeholder="Ubicación"
            showClear
          />

          <Select
            v-model="filters.categoryId"
            :options="categories"
            optionLabel="name"
            optionValue="id"
            placeholder="Categoría"
            showClear
          />
        </div>

        <div class="flex gap-2 mb-4">
          <Button
            label="Aplicar filtros"
            icon="pi pi-filter"
            @click="loadInventory"
            :loading="loadingInventory"
          />
          <Button
            label="Limpiar"
            icon="pi pi-times"
            severity="secondary"
            outlined
            @click="clearFilters"
          />
          <Button
            label="Exportar XLSX"
            icon="pi pi-file-excel"
            severity="success"
            outlined
            @click="handleExportXlsx"
            :loading="exportingXlsx"
          />
          <Button
            label="Trasladar"
            icon="pi pi-send"
            severity="info"
            outlined
            :disabled="selectedDevices.length === 0"
            @click="openTransferDrawer"
          />
          <Button
            label="Dar de baja"
            icon="pi pi-trash"
            severity="danger"
            outlined
            :disabled="selectedDevices.length === 0"
            @click="openWriteoffDrawer"
          />
        </div>

        <div class="flex items-center justify-between mb-4">
          <span class="text-sm text-surface-500">
            {{ selectedDevices.length }} dispositivo(s) seleccionado(s)
          </span>

          <Button
            label="Limpiar selección"
            icon="pi pi-times"
            severity="secondary"
            text
            :disabled="selectedDevices.length === 0"
            @click="clearSelection"
          />
        </div>

        <DataTable v-model:selection="selectedDevices" :value="devices" :loading="loadingInventory" dataKey="id" stripedRows>
          <template #empty>
            <div class="text-center py-6 text-muted-color">No hay dispositivos para mostrar.</div>
          </template>

          <Column selectionMode="multiple" headerStyle="width: 3rem" />

          <Column header="Producto">
            <template #body="{ data }">
              {{ data.product?.name ?? '—' }}
            </template>
          </Column>

          <Column header="Categoría">
            <template #body="{ data }">
              {{ data.product?.category?.name ?? '—' }}
            </template>
          </Column>

          <Column header="Código interno">
            <template #body="{ data }">
              {{ data.internalCode ?? '—' }}
            </template>
          </Column>

          <Column header="N° Serie">
            <template #body="{ data }">
              {{ data.serialNumber ?? '—' }}
            </template>
          </Column>

          <Column header="Estado">
            <template #body="{ data }">
              <DeviceStatusBadge :status="data.status?.name ?? ''" />
            </template>
          </Column>

          <Column header="Ubicación">
            <template #body="{ data }">
              {{ data.ubication?.name ?? '—' }}
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <InventoryTransferDrawer
      v-model="showTransferDrawer"
      :ubications="ubications"
      :selected-count="selectedDevices.length"
      :loading="transferring"
      @submit="handleTransfer"
    />

    <InventoryWriteoffDrawer
      v-model="showWriteoffDrawer"
      :devices="selectedDevices"
      :loading="writingOff"
      @submit="handleWriteoff"
    />
  </div>
</template>

<style scoped>
.inventory-kpi {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-width: 220px;
  padding: 0.9rem 1rem;
  border: 1px solid var(--p-content-border-color, #e5e7eb);
  border-radius: 12px;
  background: var(--p-content-background, #ffffff);
}

.inventory-kpi-icon {
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(79, 70, 229, 0.12);
  color: #4f46e5;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.inventory-kpi-content {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.inventory-kpi-label {
  font-size: 0.8rem;
  color: var(--p-text-muted-color, #6b7280);
}

.inventory-kpi-value {
  font-size: 1.6rem;
  font-weight: 700;
}
</style>