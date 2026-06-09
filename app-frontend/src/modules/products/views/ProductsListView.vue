<script setup lang="ts">
import { computed, ref, onMounted, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import type { Product, ProductPayload } from '@/types/product.types'
import type { Brand, ModelItem, Category, Status, Ubication } from '@/types/catalog.types'
import { getProducts, getProduct, createProduct, updateProduct, deleteProduct } from '@/services/product.service'
import { getBrands, getModels, getCategories, getStatuses, getUbications } from '@/services/catalog.service'
import type { DevicePayload } from '@/types/device.types'
import { createDevice } from '@/services/device.service'
import DeviceForm from '@/modules/components/DeviceForm.vue'

const router = useRouter()
const toast  = useToast()

// ── Cargar productos ──────────────────────────────────────────────────
const loading  = ref(false)
const products: Ref<Product[]> = ref([])

async function loadProducts() {
  loading.value = true
  try {
    products.value = await getProducts()
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los productos.', life: 4000 })
  } finally {
    loading.value = false
  }
}

// ── Catálogo auxiliar para los dropdowns ─────────────────────────────
const brands     = ref<Brand[]>([])
const models     = ref<ModelItem[]>([])
const categories = ref<Category[]>([])
const statuses = ref<Status[]>([])
const ubications = ref<Ubication[]>([])

async function loadCatalog() {
  const [b, m, c, s, u] = await Promise.all([
    getBrands(),
    getModels(),
    getCategories(),
    getStatuses(),
    getUbications(),
  ])

  brands.value = b
  models.value = m
  categories.value = c
  statuses.value = s
  ubications.value = u
}

// ── Drawer crear / editar ─────────────────────────────────────────────
type DrawerMode = 'create' | 'edit'

const showDrawer      = ref(false)
const drawerMode      = ref<DrawerMode>('create')
const drawerLoading   = ref(false)
const submitting      = ref(false)
const editingId       = ref<number | null>(null)
const deviceCount     = ref(0)

const emptyForm: ProductPayload = {
  name: '', brandId: null, modelId: null,
  categoryId: null, description: '', isActive: true,
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

const hasProductChanges = computed(() => {
  return (
    JSON.stringify(normalizedCurrentProductValues.value)
    !== JSON.stringify(normalizedInitialProductValues.value)
  )
})

const submitDisabled = computed(() => {
  return submitting.value || (drawerMode.value === 'edit' && !hasProductChanges.value)
})

function openCreateDrawer() {
  drawerMode.value = 'create'
  editingId.value = null
  deviceCount.value = 0
  drawerInitialValues.value = { ...emptyForm }
  drawerForm.value = { ...emptyForm }
  showDrawer.value = true
}

async function openEditDrawer(product: Product) {
  drawerMode.value  = 'edit'
  editingId.value   = product.id
  showDrawer.value  = true
  drawerLoading.value = true

  try {
    const p = await getProduct(product.id)
    const initialValues: ProductPayload = {
      name: p.name,
      brandId: p.brand?.id ?? null,
      modelId: p.model?.id ?? null,
      categoryId: p.category?.id ?? null,
      description: p.description ?? '',
      isActive: p.isActive,
    }

    drawerInitialValues.value = { ...initialValues }
    drawerForm.value = { ...initialValues }

    deviceCount.value = 0
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el producto.', life: 4000 })
    showDrawer.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function handleSubmit() {
  if (submitDisabled.value) return

  if (!drawerForm.value.name.trim()) {
    toast.add({ severity: 'warn', summary: 'Campo requerido', detail: 'El nombre del producto es obligatorio.', life: 3000 })
    return
  }

  const payload: ProductPayload = {
    ...normalizedCurrentProductValues.value,
    description: normalizedCurrentProductValues.value.description || undefined,
  }

  submitting.value = true
  try {
    if (drawerMode.value === 'create') {
      const newProduct = await createProduct(payload)
      products.value.push(newProduct)
      toast.add({ severity: 'success', summary: 'Producto creado', detail: `"${newProduct.name}" agregado correctamente.`, life: 3000 })
    } else {
      const updated = await updateProduct(editingId.value!, payload)
      const idx = products.value.findIndex(p => p.id === editingId.value)
      if (idx !== -1) products.value[idx] = updated
      toast.add({ severity: 'success', summary: 'Producto actualizado', detail: `"${updated.name}" actualizado correctamente.`, life: 3000 })
    }

    showDrawer.value = false
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo completar la operación.', life: 4000 })
  } finally {
    submitting.value = false
  }
}

// ── Eliminar producto ─────────────────────────────────────────────────
const showDeleteDialog  = ref(false)
const productToDelete: Ref<Product | null> = ref(null)

function confirmDelete(product: Product) {
  productToDelete.value  = product
  showDeleteDialog.value = true
}

async function handleDelete() {
  if (!productToDelete.value) return
  const hasDevices = (productToDelete.value as any).deviceCount > 0

  try {
    await deleteProduct(productToDelete.value.id)
    products.value = products.value.filter(p => p.id !== productToDelete.value!.id)
    toast.add({
      severity: 'success',
      summary: 'Producto eliminado',
      detail: hasDevices
        ? `"${productToDelete.value.name}" y sus dispositivos asociados fueron eliminados.`
        : `"${productToDelete.value.name}" eliminado correctamente.`,
      life: 3000,
    })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error al eliminar',
      detail: 'No se pudo eliminar el producto. Puede tener dispositivos asociados que impiden la eliminación.',
      life: 5000,
    })
  } finally {
    showDeleteDialog.value = false
    productToDelete.value  = null
  }
}

// ── Drawer agregar dispositivo desde producto ─────────────────────────
const showDeviceDrawer = ref(false)
const deviceSubmitting = ref(false)
const selectedProductForDevice = ref<Product | null>(null)

const emptyDeviceForm: DevicePayload = {
  productId: 0,
  statusId: 0,
  internalCode: null,
  serialNumber: null,
  ubicationId: null,
  observation: null,
}

const deviceInitialValues = ref<DevicePayload>({ ...emptyDeviceForm })

// ── Navegación ────────────────────────────────────────────────────────
function viewDetails(product: Product) {
  router.push({ name: 'admin-product-detail', params: { id: product.id } })
}

function addDevices(product: Product) {
  selectedProductForDevice.value = product
  deviceInitialValues.value = {
    ...emptyDeviceForm,
    productId: product.id,
  }
  showDeviceDrawer.value = true
}

// ── Submit de Dispositivo ──────────────────────────────────────────────
async function handleCreateDeviceFromProduct(payload: DevicePayload) {
  if (!selectedProductForDevice.value) return

  const normalizedPayload: DevicePayload = {
    productId: selectedProductForDevice.value.id,
    statusId: payload.statusId,
    internalCode: payload.internalCode || null,
    serialNumber: payload.serialNumber || null,
    ubicationId: payload.ubicationId || null,
    observation: payload.observation || null,
  }

  if (!normalizedPayload.productId || !normalizedPayload.statusId) {
    toast.add({
      severity: 'warn',
      summary: 'Campos requeridos',
      detail: 'El producto y el estado son obligatorios.',
      life: 3000,
    })
    return
  }

  deviceSubmitting.value = true
  try {
    await createDevice(normalizedPayload)

    toast.add({
      severity: 'success',
      summary: 'Dispositivo creado',
      detail: `Se agregó un dispositivo a "${selectedProductForDevice.value.name}".`,
      life: 3000,
    })

    showDeviceDrawer.value = false
    selectedProductForDevice.value = null
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo crear el dispositivo.',
      life: 4000,
    })
  } finally {
    deviceSubmitting.value = false
  }
}

// ── Init ──────────────────────────────────────────────────────────────
onMounted(() => {
  loadProducts()
  loadCatalog()
})
</script>

<template>
  <div class="page-container">

    <!-- Cabecera -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Productos</h1>
        <p class="page-subtitle">Gestiona los productos del inventario</p>
      </div>
      <Button icon="pi pi-plus" label="Nuevo Producto" @click="openCreateDrawer" />
    </div>

    <!-- Tabla -->
    <Card>
      <template #content>
        <DataTable :value="products" :loading="loading" dataKey="id" stripedRows>

          <template #empty>
            <div class="text-center py-6 text-muted-color">No hay productos registrados.</div>
          </template>

          <Column field="name" header="Nombre" />

          <Column header="Marca">
            <template #body="{ data }">
              {{ data.brand?.name ?? '—' }}
            </template>
          </Column>

          <Column header="Modelo">
            <template #body="{ data }">
              {{ data.model?.name ?? '—' }}
            </template>
          </Column>

          <Column header="Categoría">
            <template #body="{ data }">
              {{ data.category?.name ?? '—' }}
            </template>
          </Column>

          <Column header="Estado" style="width: 100px">
            <template #body="{ data }">
              <Tag
                :value="data.isActive ? 'Activo' : 'Inactivo'"
                :severity="data.isActive ? 'success' : 'danger'"
              />
            </template>
          </Column>

          <Column header="Acciones" style="width: 160px">
            <template #body="{ data }">
              <Button
                icon="pi pi-info-circle"
                rounded text severity="info"
                v-tooltip.top="'Ver detalles'"
                @click="viewDetails(data)"
              />
              <Button
                icon="pi pi-pencil"
                rounded text severity="secondary"
                v-tooltip.top="'Editar'"
                @click="openEditDrawer(data)"
              />
              <Button
                icon="pi pi-server"
                rounded text severity="help"
                v-tooltip.top="'Agregar dispositivos'"
                @click="addDevices(data)"
              />
              <Button
                icon="pi pi-trash"
                rounded text severity="danger"
                v-tooltip.top="'Eliminar'"
                @click="confirmDelete(data)"
              />
            </template>
          </Column>

        </DataTable>
      </template>
    </Card>

    <!-- Drawer crear / editar -->
    <Drawer
      v-model:visible="showDrawer"
      :header="drawerMode === 'create' ? 'Nuevo producto' : 'Editar producto'"
      position="right"
      style="width: 440px"
      :dismissable="!submitting"
    >
      <div v-if="drawerLoading" class="py-12 text-center text-muted-color">
        <i class="pi pi-spin pi-spinner text-2xl" />
        <p class="mt-2">Cargando datos...</p>
      </div>

      <form v-else class="flex flex-col gap-4" @submit.prevent="handleSubmit">

        <!-- Nombre -->
        <div class="flex flex-col gap-1">
          <label class="font-medium">Nombre <span class="text-red-400">*</span></label>
          <InputText v-model.trim="drawerForm.name" :disabled="submitting" />
        </div>

        <!-- Descripción -->
        <div class="flex flex-col gap-1">
          <label class="font-medium">Descripción</label>
          <Textarea v-model="drawerForm.description" rows="3" :disabled="submitting" />
        </div>

        <!-- Marca -->
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

        <!-- Modelo -->
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

        <!-- Categoría -->
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

        <!-- Estado activo -->
        <div class="flex items-center gap-2">
          <ToggleSwitch v-model="drawerForm.isActive" :disabled="submitting" />
          <label class="font-medium">Producto activo</label>
        </div>

        <!-- Contador de devices (solo en edición) -->
        <div v-if="drawerMode === 'edit'" class="devices-counter">
          <i class="pi pi-server" />
          <span>Este producto puede tener dispositivos asociados. Adminístralos desde "Ver detalles".</span>
        </div>

        <!-- Botones -->
        <div class="flex justify-end gap-2 mt-2">
          <Button type="button" label="Cancelar" severity="secondary" text :disabled="submitting" @click="showDrawer = false" />
          <Button
            type="submit"
            :label="drawerMode === 'create' ? 'Crear producto' : 'Guardar cambios'"
            icon="pi pi-check"
            :loading="submitting"
            :disabled="submitDisabled"
          />
        </div>

      </form>
    </Drawer>

    <!-- Drawer agregar dispositivo desde producto -->
    <Drawer
      v-model:visible="showDeviceDrawer"
      :header="`Nuevo dispositivo${selectedProductForDevice ? ` para ${selectedProductForDevice.name}` : ''}`"
      position="right"
      style="width: 440px"
      :dismissable="!deviceSubmitting"
    >
      <DeviceForm
        :initial-values="deviceInitialValues"
        :statuses="statuses"
        :ubications="ubications"
        :submitting="deviceSubmitting"
        :fixed-product-id="selectedProductForDevice?.id ?? null"
        mode="create"
        hide-product-field
        @submit="handleCreateDeviceFromProduct"
        @cancel="showDeviceDrawer = false"
      />
    </Drawer>

    <!-- Dialog confirmación eliminación -->
    <Dialog
      v-model:visible="showDeleteDialog"
      header="Confirmar eliminación"
      modal
      :style="{ width: '400px' }"
    >
      <div class="flex flex-col gap-3">
        <p>¿Estás seguro de que deseas eliminar <strong>{{ productToDelete?.name }}</strong>?</p>
        <Message severity="warn" :closable="false">
          Si este producto tiene dispositivos asociados, <strong>todos serán eliminados</strong> junto con el producto.
        </Message>
      </div>
      <template #footer>
        <Button label="Cancelar" severity="secondary" text @click="showDeleteDialog = false" />
        <Button label="Eliminar" severity="danger" icon="pi pi-trash" @click="handleDelete" />
      </template>
    </Dialog>

  </div>
</template>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 1.25rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.75rem; }
.page-title { font-size: 1.5rem; font-weight: 700; margin: 0; }
.page-subtitle { font-size: 0.875rem; color: var(--p-text-muted-color); margin: 0.25rem 0 0; }

.devices-counter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.9rem;
  background: var(--p-surface-50, rgba(0,0,0,0.03));
  border: 1px solid var(--p-surface-200, rgba(0,0,0,0.08));
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--p-text-muted-color);
}
</style>
