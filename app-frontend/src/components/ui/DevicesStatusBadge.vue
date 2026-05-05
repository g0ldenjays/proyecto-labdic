<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string }>()

const config = computed(() => {
  switch (props.status.toLowerCase()) {
    case 'disponible':
      return { label: 'Disponible', severity: 'success', variant: 'undefined' }
    case 'prestado':
      return { label: 'Prestado', severity: 'warn', variant: 'undefined' }
    case 'en_mantenimiento':
      return { label: 'En mantención', severity: 'danger', variant: 'undefined' }

    case 'de_baja':
      return {
        label: 'De baja',
        severity: undefined,
        style: {
          background: 'transparent',
          color: '#374151',
          border: '1px solid #6b7280',
          fontWeight: '600',
        },
      }

    case 'devuelto':
      return { label: 'Devuelto', severity: 'secondary', variant: 'undefined' }
    default:
      return { label: props.status, severity: 'secondary', variant: 'undefined' }
  }
})
</script>

<template>
  <Tag
    :value="config.label"
    :severity="config.severity"
    :style="config.style"
  />
</template>
