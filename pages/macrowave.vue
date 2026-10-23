<template>
  <AdminMacrowave v-if="unlocked" @exit="returnToAdmin" />

  <section v-else class="macrowave-login min-h-screen d-flex align-items-center justify-content-center p-4">
    <form class="card border-0 shadow-lg p-4 w-100" @submit.prevent="unlock">
      <h1 class="h4 fw-bold text-center mb-2">📊 MacroWave 總經戰情室</h1>
      <p class="text-muted text-center mb-4">請輸入管理員密碼</p>
      <input
        v-model="password"
        type="password"
        autocomplete="current-password"
        class="form-control mb-2"
        autofocus
      >
      <p v-if="errorMessage" class="text-danger small fw-bold mb-2">{{ errorMessage }}</p>
      <button type="submit" class="btn btn-primary fw-bold w-100">進入戰情室</button>
      <NuxtLink to="/admin" class="btn btn-link text-secondary mt-2">返回管理後台</NuxtLink>
    </form>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { getTodayPassword } from '@/utils/auth'

useHead({
  title: 'MacroWave 總經戰情室',
  link: [{ rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' }]
})

const macrowaveMode = useState('macrowaveMode', () => false)
const unlocked = ref(false)
const password = ref('')
const errorMessage = ref('')

macrowaveMode.value = true

onMounted(() => {
  unlocked.value = sessionStorage.getItem('macrowave_unlocked') === '1'
})

const unlock = () => {
  if (password.value !== getTodayPassword()) {
    errorMessage.value = '密碼錯誤'
    return
  }
  sessionStorage.setItem('macrowave_unlocked', '1')
  unlocked.value = true
  password.value = ''
  errorMessage.value = ''
}

const returnToAdmin = () => {
  macrowaveMode.value = false
  navigateTo('/admin')
}

onBeforeUnmount(() => {
  macrowaveMode.value = false
})
</script>

<style scoped>
.macrowave-login {
  background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 100%);
}
.macrowave-login .card { max-width: 26rem; }
</style>
