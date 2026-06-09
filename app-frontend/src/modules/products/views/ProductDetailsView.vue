<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { Product, ProductPayload } from '@/types/product.types'
import type { Device, DevicePayload } from '@/types/device.types'
import { getProduct, updateProduct } from '@/services/product.service'
import { getDevicesByProduct, createDevice } from '@/services/device.service'
import DeviceForm from '@/modules/components/DeviceForm.vue'
import type { Brand, Category, ModelItem, Status, Ubication } from '@/types/catalog.types'
import { getBrands, getCategories, getModels, getStatuses, getUbications } from '@/services/catalog.service'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const productId = Number(route.params.id)

const product = ref<Product | null>(null)
const devices = ref<Device[]>([])
const loadingProduct = ref(false)
const loadingDevices = ref(false)

const showDrawer = ref(false)
const drawerLoading = ref(false)
const submitting = ref(false)
const editingId = ref<number | null>(null)

const brands = ref<Brand[]>([])
const models = ref<ModelItem[]>([])
const categories = ref<Category[]>([])

const emptyForm: ProductPayload = {
  name: '',
  brandId: null,
  modelId: null,
  categoryId: null,
  description: '',
  isActive: true,
}

const drawerForm = ref<ProductPayload>({ ...emptyForm })
const drawerInitialValues = ref<ProductPayload>({ ...emptyForm })

function normalizeProductPayload(values: ProductPayload): ProductPayload {
  return {
    name: values.name?.trim() || '',
    brandId: values.brandId ?? null,
    modelId: values.modelId ?? null,
    categoryId: values.categoryId ?? null,
    description: values.description?.trim() || '',
    isActive: values.isActive,
  }
}

const normalizedInitialProductValues = computed(() =>
  normalizeProductPayload(drawerInitialValues.value),
)

const normalizedCurrentProductValues = computed(() =>
  normalizeProductPayload(drawerForm.value),
)

const hasProductChanges = computed(() =>
  JSON.stringify(normalizedCurrentProductValues.value) !==
  JSON.stringify(normalizedInitialProductValues.value),
)

const submitDisabled = computed(() => submitting.value || !hasProductChanges.value)

const showAddDeviceDialog = ref(false)
const submittingDevice = ref(false)
const statuses = ref<Status[]>([])
const ubications = ref<Ubication[]>([])

async function loadProduct() {
  loadingProduct.value = true
  try {
    product.value = await getProduct(productId)
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el producto.',
      life: 4000,
    })
    router.push({ name: 'admin-products' })
  } finally {
    loadingProduct.value = false
  }
}

async function loadDeviceAuxData() {
  try {
    const [s, u] = await Promise.all([getStatuses(), getUbications()])
    statuses.value = s
    ubications.value = u
  } catch {
    statuses.value = []
    ubications.value = []
  }
}

async function loadCatalog() {
  try {
    const [b, m, c] = await Promise.all([
      getBrands(),
      getModels(),
      getCategories(),
    ])
    brands.value = b
    models.value = m
    categories.value = c
  } catch {
    brands.value = []
    models.value = []
    categories.value = []
  }
}

async function loadDevices() {
  loadingDevices.value = true
  try {
    devices.value = await getDevicesByProduct(productId)
  } catch {
    // Si la fase 4 no está lista aún, no rompe la vista
    devices.value = []
  } finally {
    loadingDevices.value = false
  }
}

function openEditDrawer() {
  if (!product.value) return

  editingId.value = product.value.id
  drawerLoading.value = true
  showDrawer.value = true

  const initialValues: ProductPayload = {
    name: product.value.name,
    brandId: product.value.brand?.id ?? null,
    modelId: product.value.model?.id ?? null,
    categoryId: product.value.category?.id ?? null,
    description: product.value.description ?? '',
    isActive: product.value.isActive,
  }

  drawerInitialValues.value = { ...initialValues }
  drawerForm.value = { ...initialValues }
  drawerLoading.value = false
}

async function handleUpdateProduct() {
  if (!product.value || !editingId.value) return

  if (!drawerForm.value.name.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Campo requerido',
      detail: 'El nombre del producto es obligatorio.',
      life: 3000,
    })
    return
  }

  const payload: ProductPayload = {
    ...normalizedCurrentProductValues.value,
    description: normalizedCurrentProductValues.value.description || undefined,
  }

  submitting.value = true
  try {
    const updated = await updateProduct(editingId.value, payload)
    product.value = updated

    drawerInitialValues.value = {
      name: updated.name,
      brandId: updated.brand?.id ?? null,
      modelId: updated.model?.id ?? null,
      categoryId: updated.category?.id ?? null,
      description: updated.description ?? '',
      isActive: updated.isActive,
    }
    drawerForm.value = { ...drawerInitialValues.value }

    toast.add({
      severity: 'success',
      summary: 'Producto actualizado',
      detail: `"${updated.name}" actualizado correctamente.`,
      life: 3000,
    })

    showDrawer.value = false
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo actualizar el producto.',
      life: 4000,
    })
  } finally {
    submitting.value = false
  }
}

function addDevices() {
  showAddDeviceDialog.value = true
}

onMounted(() => {
  if (Number.isNaN(productId)) {
    router.push({ name: 'admin-products' })
    return
  }
  loadCatalog()
  loadProduct()
  loadDeviceAuxData()
  loadDevices()
})

async function handleCreateDevice(payload: DevicePayload) {
  if (!product.value) return

  if (!payload.statusId) {
    toast.add({
      severity: 'warn',
      summary: 'Campo requerido',
      detail: 'El estado es obligatorio.',
      life: 3000,
    })
    return
  }

  submittingDevice.value = true
  try {
    await createDevice({
      ...payload,
      productId: product.value.id,
    })

    toast.add({
      severity: 'success',
      summary: 'Dispositivo creado',
      detail: 'El dispositivo fue agregado correctamente.',
      life: 3000,
    })

    showAddDeviceDialog.value = false
    await loadDevices()
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo crear el dispositivo.',
      life: 4000,
    })
  } finally {
    submittingDevice.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <!-- Botón volver -->
    <div>
      <Button
        icon="pi pi-arrow-left"
        label="Volver a Productos"
        severity="secondary"
        text
        @click="router.push({ name: 'admin-products' })"
      />
    </div>

    <!-- Skeleton mientras carga -->
    <div v-if="loadingProduct" class="flex flex-col gap-3">
      <Skeleton height="2rem" width="40%" />
      <Skeleton height="1rem" width="60%" />
      <Skeleton height="200px" />
    </div>

    <template v-else-if="product">
      <!-- Info del producto -->
      <Card>
        <template #title>
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center gap-3">
              <span class="product-name">{{ product.name }}</span>
              <Tag
                :value="product.isActive ? 'Activo' : 'Inactivo'"
                :severity="product.isActive ? 'success' : 'danger'"
              />
            </div>
            <Button
              icon="pi pi-pencil"
              label="Editar producto"
              severity="secondary"
              outlined
              size="small"
              @click="openEditDrawer"
            />
          </div>
        </template>

        <template #content>
          <div class="product-grid">
            <div class="detail-row">
              <span class="detail-label">Descripción</span>
              <span class="detail-value">{{ product.description ?? '—' }}</span>
            </div>

            <div class="detail-row">
              <span class="detail-label">Marca</span>
              <span class="detail-value">{{ product.brand?.name ?? '—' }}</span>
            </div>

            <div class="detail-row">
              <span class="detail-label">Modelo</span>
              <span class="detail-value">{{ product.model?.name ?? '—' }}</span>
            </div>

            <div class="detail-row">
              <span class="detail-label">Categoría</span>
              <span class="detail-value">{{ product.category?.name ?? '—' }}</span>
            </div>

            <div class="detail-row">
              <span class="detail-label">Creado</span>
              <span class="detail-value">{{
                new Date(product.createdAt).toLocaleDateString('es-CL')
              }}</span>
            </div>
          </div>
        </template>
      </Card>

      <!-- Dispositivos asociados -->
      <Card>
        <template #title>
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center gap-2">
              <i class="pi pi-server" />
              <span>Dispositivos asociados</span>
              <Badge :value="devices.length" />
            </div>
            <Button
              icon="pi pi-plus"
              label="Agregar dispositivo"
              size="small"
              @click="addDevices"
            />
          </div>
        </template>

        <template #content>
          <DataTable
            :value="devices"
            :loading="loadingDevices"
            dataKey="id"
            stripedRows
            size="small"
          >
            <template #empty>
              <div class="text-center py-6 text-muted-color">
                <i class="pi pi-server text-3xl mb-2 block opacity-30" />
                Este producto no tiene dispositivos asociados aún.
              </div>
            </template>

            <Column field="internalCode" header="Código interno">
              <template #body="{ data }">{{ data.internalCode ?? '—' }}</template>
            </Column>

            <Column field="serialNumber" header="N° Serie">
              <template #body="{ data }">{{ data.serialNumber ?? '—' }}</template>
            </Column>

            <Column header="Estado">
              <template #body="{ data }">
                <Tag :value="data.status?.name ?? '—'" severity="secondary" />
              </template>
            </Column>

            <Column header="Ubicación">
              <template #body="{ data }">{{ data.ubication?.name ?? '—' }}</template>
            </Column>

            <Column field="createdAt" header="Agregado">
              <template #body="{ data }">
                {{ new Date(data.createdAt).toLocaleDateString('es-CL') }}
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>

      <!-- Drawer editar producto -->
      <Drawer
        v-model:visible="showDrawer"
        header="Editar producto"
        position="right"
        style="width: 440px"
        :dismissable="!submitting"
      >
        <div v-if="drawerLoading" class="py-12 text-center text-muted-color">
          <i class="pi pi-spin pi-spinner text-2xl" />
          <p class="mt-2">Cargando datos...</p>
        </div>

        <form v-else class="flex flex-col gap-4" @submit.prevent="handleUpdateProduct">
          <div class="flex flex-col gap-1">
            <label class="font-medium">Nombre <span class="text-red-400">*</span></label>
            <InputText v-model.trim="drawerForm.name" :disabled="submitting" />
          </div>

          <div class="flex flex-col gap-1">
            <label class="font-medium">Descripción</label>
            <Textarea v-model="drawerForm.description" rows="3" :disabled="submitting" />
          </div>

          <div class="flex flex-col gap-1">
            <label class="font-medium">Marca</label>
            <Select
              v-model="drawerForm.brandId"
              :options="brands"
              optionLabel="name"
              optionValue="id"
              placeholder="Selecciona una marca"
              showClear
              :disabled="submitting"
            />
          </div>

          <div class="flex flex-col gap-1">
            <label class="font-medium">Modelo</label>
            <Select
              v-model="drawerForm.modelId"
              :options="models"
              optionLabel="name"
              optionValue="id"
              placeholder="Selecciona un modelo"
              showClear
              :disabled="submitting"
            />
          </div>

          <div class="flex flex-col gap-1">
            <label class="font-medium">Categoría</label>
            <Select
              v-model="drawerForm.categoryId"
              :options="categories"
              optionLabel="name"
              optionValue="id"
              placeholder="Selecciona una categoría"
              showClear
              :disabled="submitting"
            />
          </div>

          <div class="flex items-center gap-2">
            <ToggleSwitch v-model="drawerForm.isActive" :disabled="submitting" />
            <label class="font-medium">Producto activo</label>
          </div>

          <div class="devices-counter">
            <i class="pi pi-server" />
            <span>Este producto puede tener dispositivos asociados. Adminístralos desde "Ver detalles".</span>
          </div>

          <div class="flex justify-end gap-2 mt-2">
            <Button
              type="button"
              label="Cancelar"
              severity="secondary"
              text
              :disabled="submitting"
              @click="showDrawer = false"
            />
            <Button
              type="submit"
              label="Guardar cambios"
              icon="pi pi-check"
              :loading="submitting"
              :disabled="submitDisabled"
            />
          </div>
        </form>
      </Drawer>

      <!-- Dialogo para agregar dispositivo -->
      <Dialog
        v-model:visible="showAddDeviceDialog"
        header="Agregar dispositivo"
        modal
        :style="{ width: '32rem' }"
      >
        <DeviceForm
          :initial-values="{
            productId: product.id,
            statusId: 0,
            internalCode: null,
            serialNumber: null,
            ubicationId: null,
          }"
          :statuses="statuses"
          :ubications="ubications"
          :fixed-product-id="product.id"
          :hide-product-field="true"
          :submitting="submittingDevice"
          @submit="handleCreateDevice"
          @cancel="showAddDeviceDialog = false"
        />
      </Dialog>
    </template>
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.product-name {
  font-size: 1.25rem;
  font-weight: 700;
}

.product-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.detail-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--p-surface-100, rgba(0, 0, 0, 0.05));
}
.detail-row:last-child {
  border-bottom: none;
}
.detail-label {
  font-weight: 600;
  color: var(--p-text-muted-color);
  font-size: 0.875rem;
}
.detail-value {
  font-size: 0.875rem;
}
.devices-counter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.9rem;
  background: var(--p-surface-50, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--p-surface-200, rgba(0, 0, 0, 0.08));
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--p-text-muted-color);
}
</style>
