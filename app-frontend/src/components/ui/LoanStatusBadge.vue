<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string }>()

const config = computed(() => {
  switch (props.status.toLowerCase()) {
    case 'pendiente':
      return { label: 'Pendiente',  severity: 'warn' }
    case 'aprobado':
    case 'prestado':
      return { label: 'Aprobado',   severity: 'success' }
    case 'rechazado':
      return { label: 'Rechazado',  severity: 'danger' }
    case 'devuelto':
      return { label: 'Devuelto',   severity: 'secondary' }
    default:
      return { label: props.status, severity: 'secondary' }
  }
})
</script>

<template>
  <Tag :value="config.label" :severity="config.severity" />
</template>
