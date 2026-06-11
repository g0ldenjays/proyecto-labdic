<script setup lang="ts">
import { ref, onMounted, type Ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import type { LoanRequest } from '@/types/loan.types'
import { getDevice } from '@/services/device.service'
import { getMyLoans, getLoan } from '@/services/loan.service'
import LoanStatusBadge from '@/components/ui/LoanStatusBadge.vue'

const toast = useToast()

const loading = ref(false)
const loans: Ref<LoanRequest[]> = ref([])

async function loadLoans() {
  loading.value = true
  try {
    loans.value = await getMyLoans()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron cargar tus solicitudes.',
      life: 4000,
    })
  } finally {
    loading.value = false
  }
}

const showDrawer = ref(false)
const drawerLoading = ref(false)
const selectedLoan: Ref<LoanRequest | null> = ref(null)

async function openDetail(loan: LoanRequest) {
  showDrawer.value = true
  drawerLoading.value = true
  try {
    selectedLoan.value = await getLoan(loan.id)

    // Enriquecer los items con los datos del device
    if (selectedLoan.value.loanRequestItems?.length) {
      const devices = await Promise.all(
        selectedLoan.value.loanRequestItems.map((item) => getDevice(item.deviceId)),
      )
      selectedLoan.value.loanRequestItems = selectedLoan.value.loanRequestItems.map(
        (item, idx) => ({ ...item, device: devices[idx] }),
      )
    }
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el detalle.',
      life: 4000,
    })
    showDrawer.value = false
  } finally {
    drawerLoading.value = false
  }
}

function getTimeline(loan: LoanRequest) {
  const isRejected = loan.status.name === 'rechazado'
  const isInCourse = ['aprobado', 'prestado', 'devuelto'].includes(loan.status.name)

  return [
    {
      label: 'Solicitud enviada',
      date: loan.requestDate,
      done: true,
      icon: 'pi pi-file-edit',
    },
    {
      label: isRejected ? 'Solicitud rechazada' : 'Préstamo en curso',
      date: loan.deliveryDate ?? null,
      done: isInCourse || isRejected,
      icon: isRejected ? 'pi pi-times-circle' : 'pi pi-check-circle',
      isReject: isRejected,
    },
    {
      label: 'Elementos devueltos',
      date: loan.actualReturnDate ?? null,
      done: loan.status.name === 'devuelto',
      icon: 'pi pi-undo',
    },
  ]
}

function formatDate(dateStr: string | null) {
  if (!dateStr) return null
  return new Date(dateStr).toLocaleDateString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(loadLoans)
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">Mis Solicitudes</h1>
        <p class="page-subtitle">Historial de tus solicitudes de préstamo</p>
      </div>
      <Button
        icon="pi pi-plus"
        label="Nueva solicitud"
        @click="$router.push({ name: 'catalog' })"
      />
    </div>

    <Card>
      <template #content>
        <DataTable :value="loans" :loading="loading" dataKey="id" stripedRows>
          <template #empty>
            <div class="text-center py-8 text-muted-color">
              <i class="pi pi-file-edit text-4xl block mb-3 opacity-30" />
              No tienes solicitudes de préstamo aún.
              <div class="mt-2">
                <Button
                  label="Ir al catálogo"
                  severity="secondary"
                  outlined
                  size="small"
                  @click="$router.push({ name: 'catalog' })"
                />
              </div>
            </div>
          </template>

          <Column field="id" header="#" style="width: 60px" />

          <Column header="Estado" style="width: 130px">
            <template #body="{ data }">
              <LoanStatusBadge :status="data.status?.name ?? ''" />
            </template>
          </Column>

          <Column header="Dispositivos" style="width: 120px">
            <template #body="{ data }">
              <span class="device-count">
                <i class="pi pi-server mr-1" />{{ data.loanRequestItems?.length ?? 0 }}
              </span>
            </template>
          </Column>

          <Column header="Motivo">
            <template #body="{ data }">
              <span class="text-sm">{{ data.reason ?? '—' }}</span>
            </template>
          </Column>

          <Column header="Fecha solicitud">
            <template #body="{ data }">{{ formatDate(data.requestDate) }}</template>
          </Column>

          <Column header="Dev. estimada">
            <template #body="{ data }">
              {{ data.estimatedReturnDate ? formatDate(data.estimatedReturnDate) : '—' }}
            </template>
          </Column>

          <Column header="" style="width: 60px">
            <template #body="{ data }">
              <Button
                icon="pi pi-eye"
                rounded
                text
                severity="info"
                v-tooltip.top="'Ver detalle'"
                @click="openDetail(data)"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Drawer -->
    <Drawer
      v-model:visible="showDrawer"
      header="Detalle de solicitud"
      position="right"
      style="width: 480px"
    >
      <div v-if="drawerLoading" class="py-12 text-center text-muted-color">
        <i class="pi pi-spin pi-spinner text-2xl" />
        <p class="mt-2">Cargando...</p>
      </div>

      <div v-else-if="selectedLoan" class="drawer-content">
        <div class="loan-header">
          <div class="flex items-center gap-2">
            <span class="loan-id">Solicitud #{{ selectedLoan.id }}</span>
            <LoanStatusBadge :status="selectedLoan.status?.name ?? ''" />
          </div>
          <p v-if="selectedLoan.reason" class="loan-reason">{{ selectedLoan.reason }}</p>
        </div>



        <div class="dates-grid">
          <div class="date-item">
            <span class="date-label">Fecha solicitud</span>
            <span class="date-value">{{ formatDate(selectedLoan.requestDate) }}</span>
          </div>
          <div v-if="selectedLoan.estimatedReturnDate" class="date-item">
            <span class="date-label">Dev. estimada</span>
            <span class="date-value">{{ formatDate(selectedLoan.estimatedReturnDate) }}</span>
          </div>
          <div v-if="selectedLoan.deliveryDate" class="date-item">
            <span class="date-label">Entregado</span>
            <span class="date-value">{{ formatDate(selectedLoan.deliveryDate) }}</span>
          </div>
          <div v-if="selectedLoan.actualReturnDate" class="date-item">
            <span class="date-label">Devuelto</span>
            <span class="date-value">{{ formatDate(selectedLoan.actualReturnDate) }}</span>
          </div>
        </div>

        <div class="section-title">Estado de la solicitud</div>
        <div class="timeline">
          <div
            v-for="(step, idx) in getTimeline(selectedLoan)"
            :key="idx"
            class="timeline-step"
            :class="{ done: step.done, reject: step.isReject }"
          >
            <div class="timeline-icon"><i :class="step.icon" /></div>
            <div class="timeline-body">
              <span class="timeline-label">{{ step.label }}</span>
              <span v-if="step.date" class="timeline-date">{{ formatDate(step.date) }}</span>
            </div>
            <div v-if="idx < 3" class="timeline-line" />
          </div>
        </div>

        <div class="section-title">
          Dispositivos <Badge :value="selectedLoan.loanRequestItems?.length ?? 0" />
        </div>
        <div class="devices-list">
          <div v-for="item in selectedLoan.loanRequestItems" :key="item.id" class="device-item">
            <i class="pi pi-server text-muted-color" />
            <div class="device-info">
              <span class="device-name">{{ item.device?.product?.name ?? '—' }}</span>
              <span class="device-code">{{
                item.device?.internalCode ?? `#${item.deviceId}`
              }}</span>
            </div>
          </div>
        </div>
        <div v-if="selectedLoan.additionalItems" class="section-title">Elementos adicionales</div>
        <div v-if="selectedLoan.additionalItems" class="additional-items-box">
          {{ selectedLoan.additionalItems }}
        </div>
      </div>
    </Drawer>
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
.device-count {
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
}
.drawer-content {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 0.25rem 0;
}
.loan-header {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.loan-id {
  font-weight: 700;
  font-size: 1rem;
}
.loan-reason {
  font-size: 0.875rem;
  color: var(--p-text-muted-color);
  margin: 0;
}
.dates-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.date-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.date-label {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.date-value {
  font-size: 0.875rem;
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
.timeline {
  display: flex;
  flex-direction: column;
}
.timeline-step {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  position: relative;
  padding-bottom: 1.25rem;
}
.timeline-step:last-child {
  padding-bottom: 0;
}
.timeline-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--p-surface-100, #f1f5f9);
  color: var(--p-text-muted-color);
  border: 2px solid var(--p-surface-200, #e2e8f0);
  font-size: 0.85rem;
  position: relative;
  z-index: 1;
}
.timeline-step.done .timeline-icon {
  background: var(--p-green-100, #dcfce7);
  color: var(--p-green-600, #16a34a);
  border-color: var(--p-green-300, #86efac);
}
.timeline-step.reject .timeline-icon {
  background: var(--p-red-100, #fee2e2);
  color: var(--p-red-600, #dc2626);
  border-color: var(--p-red-300, #fca5a5);
}
.timeline-body {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding-top: 0.35rem;
}
.timeline-label {
  font-size: 0.875rem;
  font-weight: 500;
}
.timeline-date {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
}
.timeline-line {
  position: absolute;
  left: 15px;
  top: 32px;
  width: 2px;
  height: calc(100% - 16px);
  background: var(--p-surface-200, #e2e8f0);
  z-index: 0;
}
.timeline-step.done .timeline-line {
  background: var(--p-green-200, #bbf7d0);
}
.devices-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.device-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  background: var(--p-surface-50, rgba(0, 0, 0, 0.02));
  border: 1px solid var(--p-surface-100, rgba(0, 0, 0, 0.05));
}
.device-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}
.device-name {
  font-size: 0.875rem;
  font-weight: 500;
}
.device-code {
  font-size: 0.75rem;
  color: var(--p-text-muted-color);
}
.additional-items-box {
  padding: 0.75rem;
  border-radius: 8px;
  background: var(--p-surface-50, rgba(0, 0, 0, 0.02));
  border: 1px solid var(--p-surface-100, rgba(0, 0, 0, 0.05));
  white-space: pre-wrap;
  font-size: 0.875rem;
}
</style>
