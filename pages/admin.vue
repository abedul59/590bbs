<template>
  <div class="mt-10 bg-white p-6 md:p-10 rounded-xl shadow-lg transition-colors duration-300 relative">
    
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">後台管理中心</h2>
      <button v-if="isAuthenticated" @click="logout" class="text-gray-500 hover:text-red-600 text-sm font-bold flex items-center gap-1">
        🚪 登出
      </button>
    </div>

    <div v-if="!isAuthenticated" class="space-y-4 max-w-md mx-auto py-10">
      <label class="block text-sm font-medium text-gray-700">請輸入今日動態密碼</label>
      <input 
        v-model="inputPassword" 
        type="password" 
        class="border border-gray-300 rounded p-3 w-full focus:outline-none focus:ring-2 focus:ring-blue-500" 
        @keyup.enter="login"
      >
      <p v-if="errorMsg" class="text-red-500 text-sm font-bold">{{ errorMsg }}</p>
      <button @click="login" class="bg-gray-800 hover:bg-gray-900 text-white px-4 py-3 rounded w-full font-bold transition">
        登入系統
      </button>
    </div>

    <div v-else class="space-y-10 animate-fade-in bg-gray-50 p-4 rounded-xl">
      <AdminSystem />
      
      <AdminTelegram />
      
      <AdminPrivate />
      
      <AdminPublic />
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getTodayPassword } from '@/utils/auth'

const isAuthenticated = ref(false)
const inputPassword = ref('')
const errorMsg = ref('')

const login = () => {
  const correctPassword = getTodayPassword()
  if (inputPassword.value === correctPassword) {
    isAuthenticated.value = true
    errorMsg.value = ''
  } else {
    errorMsg.value = '密碼錯誤！請確認今日動態密碼。'
  }
}

const logout = () => {
  isAuthenticated.value = false
  inputPassword.value = ''
  navigateTo('/') // 登出返回首頁
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
</style>