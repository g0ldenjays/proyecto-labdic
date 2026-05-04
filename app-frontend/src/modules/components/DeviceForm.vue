<!-- src/modules/devices/components/DeviceForm.vue -->
<script setup lang="ts">
import { ref, watch } from 'vue'
import type { DevicePayload } from '@/types/device.types'
import type { Product } from '@/types/product.types'
import type { Status, Ubication } from '@/types/catalog.types'

const props = withDefaults(
  defineProps<{
    initialValues: DevicePayload
    products?: Product[]
    statuses: Status[]
    ubications: Ubication[]
    submitting?: boolean
    fixedProductId?: number | null
    hideProductField?: boolean
  }>(),
  {
    products: () => [],
    submitting: false,
    fixedProductId: null,
    hideProductField: false,
  },
)

const emit = defineEmits<{
  (e: 'submit', payload: DevicePayload): void
  (e: 'cancel'): void
}>()

function buildForm(values: DevicePayload): DevicePayload {
  return {
    productId: props.fixedProductId ?? values.productId ?? 0,
    statusId: values.statusId ?? 0,
    internalCode: values.internalCode ?? null,
    serialNumber: values.serialNumber ?? null,
    ubicationId: values.ubicationId ?? null,
  }
}

const form = ref<DevicePayload>(buildForm(props.initialValues))

watch(
  () => [props.initialValues, props.fixedProductId],
  () => {
    form.value = buildForm(props.initialValues)
  },
  { deep: true, immediate: true },
)

function onSubmit() {
  emit('submit', {
    ...form.value,
    productId: props.fixedProductId ?? form.value.productId,
  })
}
</script>

<template>
  <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
    <!-- Producto -->
    <div v-if="!hideProductField" class="flex flex-col gap-1">
      <label class="font-medium">Producto <span class="text-red-400">*</span></label>
      <Select
        v-model="form.productId"
        :options="products"
        optionLabel="name"
        optionValue="id"
        placeholder="Selecciona un producto"
        filter
        :disabled="submitting || !!fixedProductId"
      />
    </div>

    <!-- Estado -->
    <div class="flex flex-col gap-1">
      <label class="font-medium">Estado <span class="text-red-400">*</span></label>
      <Select
        v-model="form.statusId"
        :options="statuses"
        optionLabel="name"
        optionValue="id"
        placeholder="Selecciona un estado"
        :disabled="submitting"
      />
    </div>

    <!-- Código interno -->
    <div class="flex flex-col gap-1">
      <label class="font-medium">Código interno</label>
      <InputText
        v-model.trim="form.internalCode"
        placeholder="Ej: 7467122111293"
        :disabled="submitting"
      />
    </div>

    <!-- Número de serie -->
    <div class="flex flex-col gap-1">
      <label class="font-medium">Número de serie</label>
      <InputText
        v-model.trim="form.serialNumber"
        placeholder="Ej: SN123456789"
        :disabled="submitting"
      />
    </div>

    <!-- Ubicación -->
    <div class="flex flex-col gap-1">
      <label class="font-medium">Ubicación</label>
      <Select
        v-model="form.ubicationId"
        :options="ubications"
        optionLabel="name"
        optionValue="id"
        placeholder="Selecciona una ubicación"
        showClear
        :disabled="submitting"
      />
    </div>

    <!-- Botones -->
    <div class="flex justify-end gap-2 mt-2">
      <Button
        type="button"
        label="Cancelar"
        severity="secondary"
        text
        :disabled="submitting"
        @click="emit('cancel')"
      />
      <Button type="submit" label="Guardar" icon="pi pi-check" :loading="submitting" />
    </div>
  </form>
</template>
