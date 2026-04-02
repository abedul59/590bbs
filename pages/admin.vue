<template>
  <div class="mt-10 bg-white p-4 md:p-8 rounded-xl shadow-lg transition-colors duration-300 relative min-h-[80vh]">
    
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">後台管理中心</h2>
      <button v-if="isAuthenticated" @click="logout" class="text-gray-500 hover:text-red-600 text-sm font-bold flex items-center gap-1 transition">
        🚪 登出
      </button>
    </div>

    <div v-if="!isAuthenticated" class="space-y-4 max-w-md mx-auto py-20">
      <label class="block text-sm font-medium text-gray-700">請輸入今日動態密碼</label>
      <input 
        v-model="inputPassword" 
        type="password" 
        class="border border-gray-300 rounded-lg p-3 w-full focus:outline-none focus:ring-2 focus:ring-blue-500" 
        @keyup.enter="login"
      >
      <p v-if="errorMsg" class="text-red-500 text-sm font-bold">{{ errorMsg }}</p>
      <button @click="login" class="bg-gray-800 hover:bg-gray-900 text-white px-4 py-3 rounded-lg w-full font-bold transition shadow-sm">
        登入系統
      </button>
    </div>

    <div v-else class="animate-fade-in flex flex-col h-full">
      
      <div class="flex flex-wrap gap-2 mb-6 bg-gray-100 p-1.5 rounded-xl border border-gray-200">
        <button @click="activeTab = 'AdminSystem'" :class="activeTab === 'AdminSystem' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          ⚙️ 系統設定與保活
        </button>
        <button @click="activeTab = 'AdminTelegram'" :class="activeTab === 'AdminTelegram' ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          🎙️ TG 大檔保全
        </button>
        <button @click="activeTab = 'AdminMaterial'" :class="activeTab === 'AdminMaterial' ? 'bg-white text-teal-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          📚 TG 教材中心
        </button>
        <button @click="activeTab = 'AdminPrivate'" :class="activeTab === 'AdminPrivate' ? 'bg-white text-green-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          🔒 私密雲端分頁
        </button>
        <button @click="activeTab = 'AdminPublic'" :class="activeTab === 'AdminPublic' ? 'bg-white text-orange-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          📢 前台公告與暫存
        </button>
      </div>

      <div class="bg-gray-50/50 flex-1 rounded-xl">
        <AdminSystem v-if="activeTab === 'AdminSystem'" />
        <AdminTelegram v-if="activeTab === 'AdminTelegram'" />
        <AdminMaterial v-if="activeTab === 'AdminMaterial'" />
        <AdminPrivate v-if="activeTab === 'AdminPrivate'" />
        <AdminPublic v-if="activeTab === 'AdminPublic'" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getTodayPassword } from '@/utils/auth'

const isAuthenticated = ref(false)
const inputPassword = ref('')
const errorMsg = ref('')

// 控制目前顯示哪個分頁，預設為系統設定
const activeTab = ref('AdminSystem') 

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
  activeTab.value = 'AdminSystem' // 登出後重置回首頁籤
  navigateTo('/')
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
</style>