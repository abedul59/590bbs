<template>
  <div :class="['bg-white transition-colors duration-300 relative min-h-[80vh]', activeTab === 'AdminMacrowave' ? 'm-0 min-h-screen p-0 rounded-none shadow-none' : 'mt-10 p-4 md:p-8 rounded-xl shadow-lg']">
    
    <div v-if="activeTab !== 'AdminMacrowave'" class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">後台管理中心</h2>
      <button v-if="isAuthenticated" @click="logout" class="text-gray-500 hover:text-red-600 text-sm font-bold flex items-center gap-1 transition">
        🚪 登出
      </button>
    </div>

    <div v-if="!isAuthenticated" class="space-y-4 max-w-md mx-auto py-20">
      <label class="block text-sm font-medium text-gray-700">輸入管理員密碼</label>
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
      
      <div v-if="activeTab !== 'AdminMacrowave'" class="flex flex-wrap gap-2 mb-6 bg-gray-100 p-1.5 rounded-xl border border-gray-200">
        <button @click="activeTab = 'AdminSystem'" :class="activeTab === 'AdminSystem' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          ⚙️ 系統設定與保活
        </button>
        <button @click="activeTab = 'AdminTelegram'" :class="activeTab === 'AdminTelegram' ? 'bg-white text-indigo-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          🎙️ TG 大檔保全
        </button>
        <button @click="activeTab = 'AdminCounseling'" :class="activeTab === 'AdminCounseling' ? 'bg-white text-sky-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          📝 SHJHS 輔導紀錄
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
        <button @click="activeTab = 'AdminCheckins'" :class="activeTab === 'AdminCheckins' ? 'bg-white text-purple-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">
          📅 打卡與喚醒紀錄
        </button>

        <button @click="activeTab = 'AdminCron'" :class="activeTab === 'AdminCron' ? 'bg-white text-amber-700 shadow-sm' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-200/50'" class="flex-1 md:flex-none px-4 py-2.5 rounded-lg font-bold text-sm transition-all duration-200">⏰ 定時排程</button>
        <button type="button" class="ml-auto px-3 py-2 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100" @click="openPrivateConsole">
          ● 系統狀態正常
        </button>
      </div>

      <div class="bg-gray-50/50 flex-1 rounded-xl">
        <AdminSystem v-if="activeTab === 'AdminSystem'" />
        <AdminTelegram v-if="activeTab === 'AdminTelegram'" />
        <AdminCounseling v-if="activeTab === 'AdminCounseling'" />
        <AdminMaterial v-if="activeTab === 'AdminMaterial'" />
        <AdminPrivate v-if="activeTab === 'AdminPrivate'" />
        <AdminPublic v-if="activeTab === 'AdminPublic'" />
        <AdminCheckins v-if="activeTab === 'AdminCheckins'" />
        <AdminCron v-if="activeTab === 'AdminCron'" />
        <LazyAdminMacrowave v-if="activeTab === 'AdminMacrowave'" @exit="closePrivateConsole" />
      </div>

    </div>

    <div v-if="showPrivateLogin" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 p-4" @click.self="closePrivateLogin">
      <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
        <h3 class="mb-5 text-lg font-bold text-gray-900">輸入管理員密碼</h3>
        <input
          ref="privatePasswordInput"
          v-model="privatePassword"
          type="password"
          autocomplete="current-password"
          class="w-full rounded-lg border border-gray-300 p-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
          @keyup.enter="unlockPrivateConsole"
        >
        <p v-if="privateError" class="mt-2 text-sm font-bold text-red-500">{{ privateError }}</p>
        <div class="mt-5 flex justify-end gap-2">
          <button type="button" class="rounded-lg bg-gray-100 px-4 py-2 font-bold text-gray-700" @click="closePrivateLogin">取消</button>
          <button type="button" class="rounded-lg bg-gray-900 px-4 py-2 font-bold text-white" @click="unlockPrivateConsole">確認</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from 'vue'
import { getTodayPassword } from '@/utils/auth'

const isAuthenticated = ref(false)
const inputPassword = ref('')
const errorMsg = ref('')

// 控制目前顯示哪個分頁，預設為系統設定
const activeTab = ref('AdminSystem') 
const showPrivateLogin = ref(false)
const privatePassword = ref('')
const privateError = ref('')
const privatePasswordInput = ref(null)
const macrowaveMode = useState('macrowaveMode', () => false)

const openPrivateConsole = async () => {
  privatePassword.value = ''
  privateError.value = ''
  showPrivateLogin.value = true
  await nextTick()
  privatePasswordInput.value?.focus()
}

const closePrivateLogin = () => {
  showPrivateLogin.value = false
  privatePassword.value = ''
  privateError.value = ''
}

const unlockPrivateConsole = () => {
  if (privatePassword.value !== getTodayPassword()) {
    privateError.value = '密碼錯誤'
    return
  }
  closePrivateLogin()
  activeTab.value = 'AdminMacrowave'
  macrowaveMode.value = true
}

const closePrivateConsole = () => {
  macrowaveMode.value = false
  activeTab.value = 'AdminSystem'
}

const login = () => {
  const correctPassword = getTodayPassword()
  if (inputPassword.value === correctPassword) {
    isAuthenticated.value = true
    errorMsg.value = ''
  } else {
    errorMsg.value = '密碼錯誤'
  }
}

const logout = () => {
  isAuthenticated.value = false
  inputPassword.value = ''
  closePrivateLogin()
  activeTab.value = 'AdminSystem' // 登出後重置回首頁籤
  navigateTo('/')
}

onBeforeUnmount(() => {
  macrowaveMode.value = false
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
</style>
