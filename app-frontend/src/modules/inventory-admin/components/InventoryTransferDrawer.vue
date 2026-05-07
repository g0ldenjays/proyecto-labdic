<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Ubication } from '@/types/catalog.types'
import type { InventoryTransferPayload } from '@/types/inventory-admin.types'

const props = defineProps<{
  modelValue: boolean
  ubications: Ubication[]
  selectedCount: number
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit', payload: Omit<InventoryTransferPayload, 'deviceIds'>): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

const form = ref({
  targetUbicationId: null as number | null,
  reason: '',
  observations: '',
})

function resetForm() {
  form.value = {
    targetUbicationId: null,
    reason: '',
    observations: '',
  }
}

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) resetForm()
  },
)

function close() {
  visible.value = false
}

function handleSubmit() {
  emit('submit', {
    targetUbicationId: form.value.targetUbicationId!,
    reason: form.value.reason || null,
    observations: form.value.observations || null,
  })
}
</script>

<template>
  <Drawer
    v-model:visible="visible"
    header="Registrar traslado"
    position="right"
    style="width: 30rem"
  >
    <div class="flex flex-col gap-4">
      <div class="text-sm text-surface-500">Se trasladarán {{ selectedCount }} dispositivo(s).</div>

      <div class="flex flex-col gap-1">
        <label class="font-medium">Ubicación destino</label>
        <Select
          v-model="form.targetUbicationId"
          :options="ubications"
          optionLabel="name"
          optionValue="id"
          placeholder="Selecciona una ubicación"
          :disabled="loading"
        />
      </div>

      <div class="flex flex-col gap-1">
        <label class="font-medium">Motivo</label>
        <InputText
          v-model="form.reason"
          placeholder="Ej: reorganización de inventario"
          :disabled="loading"
        />
      </div>

      <div class="flex flex-col gap-1">
        <label class="font-medium">Observaciones</label>
        <Textarea
          v-model="form.observations"
          rows="4"
          autoResize
          placeholder="Observaciones del traslado"
          :disabled="loading"
        />
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <Button label="Cancelar" severity="secondary" text :disabled="loading" @click="close" />
        <Button
          label="Registrar traslado"
          icon="pi pi-check"
          :loading="loading"
          @click="handleSubmit"
        />
      </div>
    </div>
  </Drawer>
</template>
