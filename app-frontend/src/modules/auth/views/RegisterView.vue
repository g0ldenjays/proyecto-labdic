<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { googleRegister } from '@/services/auth.service'

const router = useRouter()
const toast = useToast()

const googleCredential = ref('')
const email = ref('')
const name = ref('')
const rut = ref('')
const password = ref('')
const confirmPassword = ref('')
const submitting = ref(false)

const username = computed(() => {
  if (!email.value) return ''
  return email.value.split('@')[0]
})

function decodeJwtPayload(token: string) {
  const payload = token.split('.')[1]
  const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
  const decoded = atob(normalized)
  return JSON.parse(decoded)
}

function handleGoogleCredential(response: { credential: string }) {
  googleCredential.value = response.credential

  const payload = decodeJwtPayload(response.credential)

  email.value = payload.email ?? ''
  name.value = payload.name ?? ''

  if (!email.value.endsWith('@umag.cl')) {
    toast.add({
      severity: 'warn',
      summary: 'Correo no permitido',
      detail: 'Solo se permiten correos institucionales @umag.cl.',
      life: 4000,
    })

    googleCredential.value = ''
    email.value = ''
    name.value = ''
  }
}

function loadGoogleScript() {
  return new Promise<void>((resolve, reject) => {
    if (document.getElementById('google-identity-script')) {
      resolve()
      return
    }

    const script = document.createElement('script')
    script.id = 'google-identity-script'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject()
    document.head.appendChild(script)
  })
}

onMounted(async () => {
  await loadGoogleScript()

  window.google.accounts.id.initialize({
    client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
    callback: handleGoogleCredential,
  })

  window.google.accounts.id.renderButton(document.getElementById('google-register-button'), {
    theme: 'outline',
    size: 'large',
    width: 360,
    text: 'signup_with',
  })
})

async function handleSubmit() {
  if (!googleCredential.value) {
    toast.add({
      severity: 'warn',
      summary: 'Google requerido',
      detail: 'Primero debes validar tu correo institucional con Google.',
      life: 3000,
    })
    return
  }

  if (password.value !== confirmPassword.value) {
    toast.add({
      severity: 'warn',
      summary: 'Contraseñas distintas',
      detail: 'Las contraseñas no coinciden.',
      life: 3000,
    })
    return
  }

  submitting.value = true

  try {
    await googleRegister({
      credential: googleCredential.value,
      password: password.value,
      confirmPassword: confirmPassword.value,
      rut: rut.value || null,
    })

    toast.add({
      severity: 'success',
      summary: 'Cuenta creada',
      detail: 'Tu usuario fue creado correctamente. Ahora puedes iniciar sesión.',
      life: 4000,
    })

    router.push({ name: 'login' })
  } catch {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'No se pudo crear la cuenta.',
      life: 4000,
    })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <Card class="register-card">
      <template #content>
        <div class="register-header">
          <div class="logo-box">LD</div>

          <div>
            <h1>LabDIC</h1>
            <p>Creación de usuario</p>
          </div>
        </div>

        <div v-if="!googleCredential" class="google-section">
          <p class="help-text">Valida tu correo institucional UMAG para comenzar el registro.</p>

          <div id="google-register-button" />
        </div>

        <form v-else class="register-form" @submit.prevent="handleSubmit">
          <div class="readonly-field">
            <label>Correo validado</label>
            <InputText :modelValue="email" class="register-input" disabled />
          </div>

          <div class="readonly-field">
            <label>Usuario</label>
            <InputText :modelValue="username" class="register-input" disabled />
          </div>

          <InputText v-model="rut" class="register-input" placeholder="RUT" />

          <Password v-model="password" class="register-password" inputClass="register-input" placeholder="Contraseña" toggleMask :feedback="false" />

          <Password
            v-model="confirmPassword"
            class="register-password"
            inputClass="register-input"
            placeholder="Confirmar contraseña"
            toggleMask
            :feedback="false"
          />

          <Button label="Crear cuenta" type="submit" :loading="submitting" />

          <Button
            label="Volver al login"
            severity="secondary"
            text
            @click="router.push({ name: 'login' })"
          />
        </form>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #0f172a;
  padding: 1rem;
}

.register-card {
  width: 100%;
  max-width: 430px;
}

.register-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.logo-box {
  width: 4rem;
  height: 4rem;
  display: grid;
  place-items: center;
  border-radius: 0.9rem;
  background: linear-gradient(135deg, #6366f1, #06b6d4);
  color: white;
  font-weight: 800;
  font-size: 1.4rem;
}

.register-header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.register-header p {
  margin: 0.25rem 0 0;
  color: var(--p-text-muted-color);
  font-weight: 600;
}

.google-section,
.register-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.help-text {
  margin: 0;
  color: var(--p-text-muted-color);
}

.readonly-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.readonly-field label {
  font-size: 0.85rem;
  font-weight: 600;
}

.register-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #0f172a;
  padding: 1rem;
}

.register-card {
  width: 100%;
  max-width: 430px;
  border-radius: 0.75rem;
  background: #111827;
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: none;
  color: #f8fafc;
}

.register-card :deep(.p-card-body) {
  padding: 2.5rem;
}

.register-card :deep(.p-card-content) {
  padding: 0;
}

.register-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.logo-box {
  width: 4rem;
  height: 4rem;
  display: grid;
  place-items: center;
  border-radius: 0.65rem;
  background: linear-gradient(135deg, #6366f1, #06b6d4);
  color: white;
  font-weight: 800;
  font-size: 1.4rem;
}

.register-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #ffffff;
}

.register-header p {
  margin: 0.25rem 0 0;
  color: #cbd5e1;
  font-weight: 700;
}

.google-section,
.register-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.help-text {
  margin: 0;
  color: #cbd5e1;
  line-height: 1.5;
}

.readonly-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.readonly-field label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #f8fafc;
}

.register-input {
  width: 100%;
  height: 58px;
  border-radius: 0.45rem;
  font-size: 1rem;
  font-weight: 600;
}

.register-password {
  width: 100%;
  display: block;
}

.register-password :deep(.p-password) {
  width: 100%;
  display: block;
}

.register-password :deep(.p-inputtext) {
  width: 100%;
  height: 58px;
  border-radius: 0.45rem;
  font-size: 1rem;
  font-weight: 600;
}

.register-password :deep(.p-icon-field) {
  width: 100%;
}

.register-password :deep(.p-password-input) {
  width: 100%;
}

.register-form :deep(.p-button) {
  min-height: 58px;
  font-weight: 800;
  border-radius: 0.45rem;
}

.register-form :deep(.p-button.p-button-text) {
  color: #cbd5e1;
}

.register-form :deep(.p-button.p-button-text:hover) {
  background: rgba(148, 163, 184, 0.08);
  color: #ffffff;
}

.google-section :deep(#google-register-button) {
  width: 100%;
}

.google-section :deep(iframe) {
  width: 100% !important;
}
</style>
