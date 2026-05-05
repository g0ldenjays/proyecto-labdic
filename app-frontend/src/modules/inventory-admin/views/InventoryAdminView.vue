<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useToast } from 'primevue/usetoast'

import type { InventoryDashboard } from '@/types/inventory-admin.types'
import { getInventoryDashboard } from '@/services/inventory-admin.service'

const toast = useToast()

const loading = ref(false)
const dashboard = ref<InventoryDashboard | null>(null)

async function loadDashboard() {
  loading.value = true
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
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
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
        @click="loadDashboard"
        :loading="loading"
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
          <div v-if="loading" class="text-surface-500">Cargando...</div>
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
          <div v-if="loading" class="text-surface-500">Cargando...</div>
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
          <div v-if="loading" class="text-surface-500">Cargando...</div>
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
  </div>
</template>
