<template>
  <div class="mt-10 bg-white p-6 md:p-10 rounded-xl shadow-lg">
    <h2 class="text-2xl font-bold mb-6">後台管理</h2>

    <div v-if="!isAuthenticated" class="space-y-4">
      <label class="block text-sm font-medium text-gray-700">請輸入今日動態密碼</label>
      <input 
        v-model="inputPassword" 
        type="password" 
        class="border border-gray-300 rounded p-2 w-full focus:ring-blue-500 focus:border-blue-500"
        placeholder="YYMMDD"
        @keyup.enter="login"
      >
      <p v-if="errorMsg" class="text-red-500 text-sm">{{ errorMsg }}</p>
      <button @click="login" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full">登入</button>
    </div>

    <div v-else class="space-y-8">
      <section class="border-b pb-6">
        <h3 class="text-xl font-semibold mb-4">網站全域設定</h3>
        <div class="space-y-3">
          <input v-model="siteTitle" type="text" placeholder="網站名稱" class="border p-2 w-full rounded">
          <input v-model="marqueeText" type="text" placeholder="跑馬燈內容" class="border p-2 w-full rounded">
          <button @click="updateSettings" class="bg-green-600 text-white px-4 py-2 rounded">儲存設定</button>
        </div>
      </section>

      <section>
        <h3 class="text-xl font-semibold mb-4">新增教學內容</h3>
        <div class="space-y-3">
          <input v-model="newPost.title" type="text" placeholder="教學標題" class="border p-2 w-full rounded">
          <textarea v-model="newPost.description" placeholder="內容說明" class="border p-2 w-full rounded"></textarea>
          <input v-model="newPost.url" type="url" placeholder="超連結 (http://...)" class="border p-2 w-full rounded">
          <button @click="addPost" class="bg-blue-600 text-white px-4 py-2 rounded">發布內容</button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getTodayPassword } from '@/utils/auth'

const supabase = useSupabaseClient()

const isAuthenticated = ref(false)
const inputPassword = ref('')
const errorMsg = ref('')

// 網站設定 state
const siteTitle = ref('')
const marqueeText = ref('')

// 新增文章 state
const newPost = ref({ title: '', description: '', url: '' })

// 登入驗證
const login = () => {
  const correctPassword = getTodayPassword()
  if (inputPassword.value === correctPassword) {
    isAuthenticated.value = true
    errorMsg.value = ''
    loadSettings()
  } else {
    errorMsg.value = '密碼錯誤！請輸入台灣時間的 YYMMDD 格式。'
  }
}

// 載入當前設定
const loadSettings = async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  if (data) {
    siteTitle.value = data.title
    marqueeText.value = data.marquee_text
  }
}

// 更新設定
const updateSettings = async () => {
  await supabase.from('site_settings').upsert({ 
    id: 1, 
    title: siteTitle.value, 
    marquee_text: marqueeText.value 
  })
  alert('設定已更新，重新整理頁面即可看到變化！')
}

// 發布新教學內容
const addPost = async () => {
  if (!newPost.value.title || !newPost.value.url) {
    alert('標題與網址為必填！')
    return
  }
  await supabase.from('bulletins').insert([
    { ...newPost.value }
  ])
  alert('發布成功！')
  newPost.value = { title: '', description: '', url: '' } // 清空表單
}
</script>