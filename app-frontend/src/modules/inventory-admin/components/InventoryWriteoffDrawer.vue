<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Device } from '@/types/device.types'
import type { InventoryWriteoffPayload } from '@/types/inventory-admin.types'

const props = defineProps<{
  modelValue: boolean
  devices: Device[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit', payload: Omit<InventoryWriteoffPayload, 'deviceIds'>): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

const form = ref({
  reason: '',
  observations: '',
  confirmed: false,
})

function resetForm() {
  form.value = {
    reason: '',
    observations: '',
    confirmed: false,
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
  if (!form.value.confirmed) return

  emit('submit', {
    reason: form.value.reason || null,
    observations: form.value.observations || null,
  })
}
</script>

<template>
  <Drawer
    v-model:visible="visible"
    header="Dar de baja dispositivos"
    position="right"
    style="width: 32rem"
  >
    <div class="flex flex-col gap-4">
      <div class="text-sm text-surface-500">
        Se dará de baja a {{ devices.length }} dispositivo(s).
      </div>

      <div class="flex flex-col gap-2 max-h-48 overflow-y-auto border rounded p-3">
        <div
          v-for="device in devices"
          :key="device.id"
          class="text-sm border-b last:border-b-0 pb-2 last:pb-0"
        >
          <div class="font-medium">{{ device.product?.name ?? '—' }}</div>
          <div class="text-surface-500">
            {{ device.internalCode ?? 'Sin código' }} · {{ device.serialNumber ?? 'Sin serie' }}
          </div>
        </div>
      </div>

      <div class="flex flex-col gap-1">
        <label class="font-medium">Motivo</label>
        <InputText
          v-model="form.reason"
          placeholder="Ej: equipo obsoleto, equipo dañado, etc."
          :disabled="loading"
        />
      </div>

      <div class="flex flex-col gap-1">
        <label class="font-medium">Observaciones</label>
        <Textarea
          v-model="form.observations"
          rows="4"
          autoResize
          placeholder="Observaciones de la baja"
          :disabled="loading"
        />
      </div>

      <div class="flex items-start gap-2 p-3 border rounded">
        <Checkbox v-model="form.confirmed" binary :disabled="loading" inputId="confirm-writeoff" />
        <label for="confirm-writeoff" class="text-sm leading-5 cursor-pointer">
          Confirmo que los dispositivos seleccionados pasarán al estado
          <strong>De baja</strong>.
        </label>
      </div>

      <div class="flex justify-end gap-2 pt-2">
        <Button
          label="Cancelar"
          severity="secondary"
          text
          :disabled="loading"
          @click="close"
        />
        <Button
          label="Dar de baja"
          icon="pi pi-times-circle"
          severity="danger"
          :loading="loading"
          :disabled="!form.confirmed"
          @click="handleSubmit"
        />
      </div>
    </div>
  </Drawer>
</template>