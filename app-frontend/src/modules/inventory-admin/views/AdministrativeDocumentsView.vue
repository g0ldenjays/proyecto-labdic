<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import type { AdministrativeDocumentListItem } from '@/types/inventory-admin.types'
import {
  downloadTransferPdf,
  downloadWriteoffPdf,
  getAdministrativeDocuments,
} from '@/services/inventory-admin.service'

const toast = useToast()

const loadingDocuments = ref(false)
const administrativeDocuments = ref<AdministrativeDocumentListItem[]>([])
const downloadingDocumentId = ref<number | null>(null)

async function loadAdministrativeDocuments() {
  loadingDocuments.value = true
  try {
    const result = await getAdministrativeDocuments()
    administrativeDocuments.value = result.items
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo cargar el historial de documentos administrativos.',
      life: 4000,
    })
  } finally {
    loadingDocuments.value = false
  }
}

async function handleDownloadAdministrativeDocument(document: AdministrativeDocumentListItem) {
  downloadingDocumentId.value = document.id

  try {
    if (document.documentType === 'transfer') {
      await downloadTransferPdf(document.id)
      return
    }

    if (document.documentType === 'writeoff') {
      await downloadWriteoffPdf(document.id)
      return
    }

    toast.add({
      severity: 'warn',
      summary: 'Tipo no soportado',
      detail: 'No existe una descarga configurada para este tipo de documento.',
      life: 4000,
    })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo descargar el documento administrativo.',
      life: 4000,
    })
  } finally {
    downloadingDocumentId.value = null
  }
}

function getDocumentLabel(type: string) {
  if (type === 'transfer') return 'Traslado'
  if (type === 'writeoff') return 'Baja'
  return type
}

function getDocumentSeverity(type: string) {
  if (type === 'transfer') return 'info'
  if (type === 'writeoff') return 'danger'
  return 'secondary'
}

onMounted(loadAdministrativeDocuments)
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <h1 class="text-2xl font-bold">Documentos administrativos</h1>
        <p class="text-sm text-surface-500">
          Historial de memorándums de traslado y baja generados desde el sistema.
        </p>
      </div>

      <Button
        label="Recargar"
        icon="pi pi-refresh"
        severity="secondary"
        :loading="loadingDocuments"
        @click="loadAdministrativeDocuments"
      />
    </div>

    <Card>
      <template #content>
        <DataTable
          :value="administrativeDocuments"
          :loading="loadingDocuments"
          dataKey="id"
          stripedRows
          paginator
          :rows="10"
          :rowsPerPageOptions="[10, 20, 50]"
        >
          <template #empty>
            <div class="text-center py-6 text-muted-color">
              No hay documentos administrativos registrados.
            </div>
          </template>

          <Column header="ID">
            <template #body="{ data }">
              #{{ data.id }}
            </template>
          </Column>

          <Column header="Tipo">
            <template #body="{ data }">
              <Tag
                :value="getDocumentLabel(data.documentType)"
                :severity="getDocumentSeverity(data.documentType)"
              />
            </template>
          </Column>

          <Column header="Fecha">
            <template #body="{ data }">
              {{ new Date(data.generatedAt).toLocaleString('es-CL') }}
            </template>
          </Column>

          <Column header="Responsable">
            <template #body="{ data }">
              {{ data.generatedByUserName }}
            </template>
          </Column>

          <Column header="Origen">
            <template #body="{ data }">
              {{ data.sourceUbicationName ?? '—' }}
            </template>
          </Column>

          <Column header="Destino">
            <template #body="{ data }">
              {{ data.targetUbicationName ?? '—' }}
            </template>
          </Column>

          <Column header="Dispositivos">
            <template #body="{ data }">
              {{ data.itemsCount }}
            </template>
          </Column>

          <Column header="Motivo">
            <template #body="{ data }">
              {{ data.reason ?? '—' }}
            </template>
          </Column>

          <Column header="Acciones" style="width: 10rem">
            <template #body="{ data }">
              <Button
                label="PDF"
                icon="pi pi-download"
                severity="secondary"
                text
                :loading="downloadingDocumentId === data.id"
                @click="handleDownloadAdministrativeDocument(data)"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>