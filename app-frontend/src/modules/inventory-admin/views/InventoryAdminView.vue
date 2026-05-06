<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useToast } from 'primevue/usetoast'

import type { Category, Status, Ubication } from '@/types/catalog.types'
import type { Device } from '@/types/device.types'
import type { InventoryAdminFilters, InventoryDashboard } from '@/types/inventory-admin.types'

import { getCategories, getStatuses, getUbications } from '@/services/catalog.service'
import { getInventoryDashboard, getInventoryDevices } from '@/services/inventory-admin.service'
import DeviceStatusBadge from '@/components/ui/DevicesStatusBadge.vue'

const toast = useToast()

const loadingDashboard = ref(false)
const loadingInventory = ref(false)

const dashboard = ref<InventoryDashboard | null>(null)
const devices = ref<Device[]>([])

const statuses = ref<Status[]>([])
const ubications = ref<Ubication[]>([])
const categories = ref<Category[]>([])

const filters = ref<InventoryAdminFilters>({
  search: '',
  statusId: null,
  ubicationId: null,
  categoryId: null,
})

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
  await Promise.all([loadDashboard(), loadInventory()])
}

function clearFilters() {
  filters.value = {
    search: '',
    statusId: null,
    ubicationId: null,
    categoryId: null,
  }
  loadInventory()
}

onMounted(async () => {
  await loadCatalogs()
  await refreshAll()
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Administración de Inventario</h1>
        <p class="text-sm text-surface-500">Vista administrativa del inventario del LabDIC.</p>
      </div>

      <Button
        label="Recargar"
        icon="pi pi-refresh"
        severity="secondary"
        @click="refreshAll"
        :loading="loadingDashboard || loadingInventory"
      />
    </div>

    <Card>
      <template #content>
        <div class="flex flex-col gap-2">
          <span class="text-sm text-surface-500">Total de dispositivos</span>
          <span class="text-3xl font-bold">
            {{ dashboard?.totalDevices ?? 0 }}
          </span>
        </div>
      </template>
    </Card>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
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
        </div>

        <DataTable :value="devices" :loading="loadingInventory" dataKey="id" stripedRows>
          <template #empty>
            <div class="text-center py-6 text-muted-color">No hay dispositivos para mostrar.</div>
          </template>

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
  </div>
</template>
