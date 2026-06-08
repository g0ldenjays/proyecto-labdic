<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useUserStore } from '@/stores/user.store'
import { getProducts } from '@/services/product.service'
import { getDevices, getAvailableDevices } from '@/services/device.service'
import { getLoans, getMyLoans } from '@/services/loan.service'
import { getInventoryAlerts } from '@/services/inventory-admin.service'
import type { InventoryAlerts } from '@/types/inventory-admin.types'

const router    = useRouter()
const toast     = useToast()
const userStore = useUserStore()

const loading = ref(false)

const loadingAlerts = ref(false)
const alerts = ref<InventoryAlerts | null>(null)

// ── Métricas ──────────────────────────────────────────────────────────
const totalProducts       = ref(0)
const totalDevices        = ref(0)
const availableDevices    = ref(0)
const pendingLoans        = ref(0)
const activeLoans         = ref(0)   // prestado
const myPendingLoans      = ref(0)
const myActiveLoans       = ref(0)

async function loadMetrics() {
  loading.value = true
  try {
    if (userStore.isAdmin) {
      const [products, devices, loans] = await Promise.all([
        getProducts(),
        getDevices(),
        getLoans(),
      ])
      totalProducts.value    = products.length
      totalDevices.value     = devices.length
      availableDevices.value = devices.filter(d => d.status?.name === 'disponible').length
      pendingLoans.value     = loans.filter(l => l.status?.name === 'pendiente').length
      activeLoans.value      = loans.filter(l => l.status?.name === 'prestado').length
    } else {
      const [available, myLoans] = await Promise.all([
        getAvailableDevices(),
        getMyLoans(),
      ])
      availableDevices.value = available.length
      myPendingLoans.value   = myLoans.filter(l => l.status?.name === 'pendiente').length
      myActiveLoans.value    = myLoans.filter(l => l.status?.name === 'prestado').length
    }
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las métricas.', life: 3000 })
  } finally {
    loading.value = false
  }
}

async function loadAlerts() {
  if (!userStore.isAdmin) return

  loadingAlerts.value = true
  try {
    alerts.value = await getInventoryAlerts()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudieron cargar las alertas del inventario.',
      life: 3000,
    })
  } finally {
    loadingAlerts.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    loadMetrics(),
    loadAlerts(),
  ])
})
</script>

<template>
  <div class="page-container">

    <!-- Bienvenida -->
    <div class="welcome-banner">
      <div class="welcome-text">
        <h1 class="welcome-title">
          Bienvenido, {{ userStore.currentUser?.name ?? userStore.currentUser?.username }} 👋
        </h1>
        <p class="welcome-sub">
          {{ userStore.isAdmin ? 'Panel de administración — LabDIC Inventory' : 'Portal de préstamos — LabDIC' }}
        </p>
      </div>
    </div>

    <!-- Métricas admin -->
    <template v-if="userStore.isAdmin">
      <div class="metrics-grid">

        <div class="metric-card" @click="$router.push({ name: 'admin-products' })">
          <div class="metric-icon products">
            <i class="pi pi-tag" />
          </div>
          <div class="metric-body">
            <span class="metric-value">
              <i v-if="loading" class="pi pi-spin pi-spinner" />
              <span v-else>{{ totalProducts }}</span>
            </span>
            <span class="metric-label">Productos</span>
          </div>
        </div>

        <div class="metric-card" @click="$router.push({ name: 'admin-devices' })">
          <div class="metric-icon devices">
            <i class="pi pi-server" />
          </div>
          <div class="metric-body">
            <span class="metric-value">
              <i v-if="loading" class="pi pi-spin pi-spinner" />
              <span v-else>{{ totalDevices }}</span>
            </span>
            <span class="metric-label">Dispositivos totales</span>
          </div>
        </div>

        <div class="metric-card" @click="$router.push({ name: 'catalog' })">
          <div class="metric-icon available">
            <i class="pi pi-check-circle" />
          </div>
          <div class="metric-body">
            <span class="metric-value">
              <i v-if="loading" class="pi pi-spin pi-spinner" />
              <span v-else>{{ availableDevices }}</span>
            </span>
            <span class="metric-label">Disponibles</span>
          </div>
        </div>

        <div class="metric-card" @click="$router.push({ name: 'admin-loans' })">
          <div class="metric-icon pending">
            <i class="pi pi-clock" />
          </div>
          <div class="metric-body">
            <span class="metric-value">
              <i v-if="loading" class="pi pi-spin pi-spinner" />
              <span v-else>{{ pendingLoans }}</span>
            </span>
            <span class="metric-label">Solicitudes pendientes</span>
          </div>
        </div>

        <div class="metric-card" @click="$router.push({ name: 'admin-loans' })">
          <div class="metric-icon active">
            <i class="pi pi-send" />
          </div>
          <div class="metric-body">
            <span class="metric-value">
              <i v-if="loading" class="pi pi-spin pi-spinner" />
              <span v-else>{{ activeLoans }}</span>
            </span>
            <span class="metric-label">Préstamos activos</span>
          </div>
        </div>

      </div>

      <!-- Alertas admin -->
      <div class="admin-alerts">
        <h2 class="section-title">Alertas</h2>

        <div class="alerts-grid">
          <div class="alert-card">
            <div class="alert-card-header">
              <div class="alert-icon maintenance">
                <i class="pi pi-wrench" />
              </div>

              <div>
                <h3 class="alert-title">Mantención prolongada</h3>
                <p class="alert-subtitle">
                  {{ alerts?.maintenanceAlertDays ?? 0 }}+ días en mantención
                </p>
              </div>
            </div>

            <div v-if="loadingAlerts" class="alert-empty">
              Cargando alertas...
            </div>

            <div
              v-else-if="!alerts?.prolongedMaintenance?.length"
              class="alert-empty"
            >
              No hay dispositivos en mantención prolongada.
            </div>

            <div v-else class="alert-list">
              <div
                v-for="item in alerts?.prolongedMaintenance ?? []"
                :key="item.deviceId"
                class="alert-item"
              >
                <div class="alert-item-main">
                  <span class="alert-item-title">{{ item.productName }}</span>
                  <span class="alert-item-detail">
                    {{ item.internalCode ?? 'Sin código' }} · {{ item.serialNumber ?? 'Sin serie' }}
                  </span>
                  <span class="alert-item-detail">
                    Ubicación: {{ item.ubicationName ?? '—' }}
                  </span>
                </div>

                <Tag
                  :value="`${item.daysInMaintenance} día(s)`"
                  severity="warn"
                />
              </div>
            </div>
          </div>

          <div class="alert-card">
            <div class="alert-card-header">
              <div class="alert-icon overdue">
                <i class="pi pi-exclamation-triangle" />
              </div>

              <div>
                <h3 class="alert-title">Préstamos vencidos</h3>
                <p class="alert-subtitle">
                  Solicitudes con fecha de devolución vencida
                </p>
              </div>
            </div>

            <div v-if="loadingAlerts" class="alert-empty">
              Cargando alertas...
            </div>

            <div
              v-else-if="!alerts?.overdueLoans?.length"
              class="alert-empty"
            >
              No hay préstamos vencidos.
            </div>

            <div v-else class="alert-list">
              <div
                v-for="loan in alerts?.overdueLoans ?? []"
                :key="loan.loanId"
                class="alert-item"
              >
                <div class="alert-item-main">
                  <span class="alert-item-title">
                    Solicitud #{{ loan.loanId }} · {{ loan.userName }}
                  </span>
                  <span class="alert-item-detail">
                    @{{ loan.userUsername }}
                  </span>
                  <span class="alert-item-detail">
                    Vencimiento: {{ new Date(loan.estimatedReturnDate).toLocaleDateString('es-CL') }}
                  </span>
                </div>

                <Tag
                  :value="`${loan.daysOverdue} día(s)`"
                  severity="danger"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Accesos rápidos admin -->
      <div class="quick-access">
        <h2 class="section-title">Accesos rápidos</h2>
        <div class="quick-grid">
          <Button label="Gestionar préstamos" icon="pi pi-file-edit" outlined
            @click="$router.push({ name: 'admin-loans' })" />
          <Button label="Ver dispositivos" icon="pi pi-server" outlined severity="secondary"
            @click="$router.push({ name: 'admin-devices' })" />
          <Button label="Gestionar usuarios" icon="pi pi-users" outlined severity="secondary"
            @click="$router.push({ name: 'admin-users' })" />
          <Button label="Catálogo auxiliar" icon="pi pi-cog" outlined severity="secondary"
            @click="$router.push({ name: 'admin-catalog' })" />
        </div>
      </div>
    </template>

    <!-- Métricas usuario normal -->
    <template v-else>
      <div class="metrics-grid">

        <div class="metric-card" @click="$router.push({ name: 'catalog' })">
          <div class="metric-icon available">
            <i class="pi pi-box" />
          </div>
          <div class="metric-body">
            <span class="metric-value">
              <i v-if="loading" class="pi pi-spin pi-spinner" />
              <span v-else>{{ availableDevices }}</span>
            </span>
            <span class="metric-label">Dispositivos disponibles</span>
          </div>
        </div>

        <div class="metric-card" @click="$router.push({ name: 'my-loans' })">
          <div class="metric-icon pending">
            <i class="pi pi-clock" />
          </div>
          <div class="metric-body">
            <span class="metric-value">
              <i v-if="loading" class="pi pi-spin pi-spinner" />
              <span v-else>{{ myPendingLoans }}</span>
            </span>
            <span class="metric-label">Mis solicitudes pendientes</span>
          </div>
        </div>

        <div class="metric-card" @click="$router.push({ name: 'my-loans' })">
          <div class="metric-icon active">
            <i class="pi pi-send" />
          </div>
          <div class="metric-body">
            <span class="metric-value">
              <i v-if="loading" class="pi pi-spin pi-spinner" />
              <span v-else>{{ myActiveLoans }}</span>
            </span>
            <span class="metric-label">Mis préstamos activos</span>
          </div>
        </div>

      </div>

      <!-- Accesos rápidos usuario -->
      <div class="quick-access">
        <h2 class="section-title">¿Qué deseas hacer?</h2>
        <div class="quick-grid">
          <Button label="Ver catálogo de dispositivos" icon="pi pi-box"
            @click="$router.push({ name: 'catalog' })" />
          <Button label="Ver mis solicitudes" icon="pi pi-list" outlined severity="secondary"
            @click="$router.push({ name: 'my-loans' })" />
        </div>
      </div>
    </template>

  </div>
  <!-- Footer informativo -->
  <div class="author-footer">
    <p><strong>LabDIC Inventory</strong> © 2025 — Todos los derechos reservados</p>
    <p>Autor: Ariel López S. | Futuro ingeniero en computación</p>
    <p>Correo: arilopez@umag.cl · arielmrlpzst@gmail.com | Contacto: +56 9 4139 4363</p>
  </div>
</template>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 1.5rem; }

/* Banner de bienvenida */
.welcome-banner {
  padding: 1.5rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
  color: white;
}
.welcome-title { font-size: 1.5rem; font-weight: 700; margin: 0; }
.welcome-sub   { font-size: 0.9rem; opacity: 0.8; margin: 0.25rem 0 0; }

/* Grid de métricas */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 10px;
  background: var(--p-surface-0, #ffffff);
  border: 1px solid var(--p-surface-200, rgba(0,0,0,0.08));
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: box-shadow 150ms, transform 150ms;
}
.metric-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.metric-icon {
  width: 48px; height: 48px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
}
.metric-icon.products  { background: #ede9fe; color: #7c3aed; }
.metric-icon.devices   { background: #dbeafe; color: #2563eb; }
.metric-icon.available { background: #dcfce7; color: #16a34a; }
.metric-icon.pending   { background: #fef9c3; color: #ca8a04; }
.metric-icon.active    { background: #ffedd5; color: #ea580c; }

.metric-body { display: flex; flex-direction: column; gap: 0.2rem; min-width: 0; }
.metric-value { font-size: 1.75rem; font-weight: 700; line-height: 1; color: var(--p-text-color); }
.metric-label { font-size: 0.8rem; color: var(--p-text-muted-color); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* Accesos rápidos */
.quick-access { display: flex; flex-direction: column; gap: 0.75rem; }
.section-title { font-size: 1rem; font-weight: 700; margin: 0; color: var(--p-text-muted-color); text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.8rem; }
.quick-grid { display: flex; gap: 0.75rem; flex-wrap: wrap; }

.admin-alerts {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.alerts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.alert-card {
  padding: 1rem;
  border-radius: 10px;
  background: var(--p-surface-0, #ffffff);
  border: 1px solid var(--p-surface-200, rgba(0,0,0,0.08));
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.alert-card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.9rem;
}

.alert-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.alert-icon.maintenance {
  background: #fef9c3;
  color: #ca8a04;
}

.alert-icon.overdue {
  background: #fee2e2;
  color: #dc2626;
}

.alert-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
}

.alert-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.78rem;
  color: var(--p-text-muted-color);
}

.alert-empty {
  font-size: 0.85rem;
  color: var(--p-text-muted-color);
  padding: 0.5rem 0;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  max-height: 260px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--p-surface-200, rgba(0,0,0,0.08));
}

.alert-item-main {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.alert-item-title {
  font-size: 0.85rem;
  font-weight: 600;
}

.alert-item-detail {
  font-size: 0.78rem;
  color: var(--p-text-muted-color);
}

@media (max-width: 640px) {
  .metrics-grid { grid-template-columns: 1fr 1fr; }
  .welcome-title { font-size: 1.2rem; }
  .alerts-grid { grid-template-columns: 1fr; }
}
.author-footer {
  margin-top: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--p-surface-200, rgba(0,0,0,0.08));
  font-size: 0.8rem;
  color: var(--p-text-muted-color);
  line-height: 1.8;
}
</style>
