<template>
  <div class="mt-10 bg-white p-6 md:p-10 rounded-xl shadow-lg">
    <h2 class="text-2xl font-bold mb-6">後台管理</h2>

    <div v-if="!isAuthenticated" class="space-y-4">
      <label class="block text-sm font-medium text-gray-700">請輸入今日動態密碼</label>
      <input 
        v-model="inputPassword" 
        type="password" 
        class="border border-gray-300 rounded p-2 w-full focus:ring-blue-500 focus:border-blue-500"
        @keyup.enter="login"
      >
      <p v-if="errorMsg" class="text-red-500 text-sm">{{ errorMsg }}</p>
      <button @click="login" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full transition duration-200">
        登入
      </button>
    </div>

    <div v-else class="space-y-8">
      
      <section class="border-b pb-6">
        <h3 class="text-xl font-semibold mb-4">網站全域設定</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm text-gray-600 mb-1">網站名稱</label>
            <input v-model="siteTitle" type="text" placeholder="例如：我的教學佈告欄" class="border border-gray-300 p-2 w-full rounded focus:ring-blue-500 focus:border-blue-500">
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">跑馬燈內容</label>
            <input v-model="marqueeText" type="text" placeholder="例如：歡迎同學！請點擊下方連結..." class="border border-gray-300 p-2 w-full rounded focus:ring-blue-500 focus:border-blue-500">
          </div>
          <button @click="updateSettings" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition duration-200">
            儲存設定
          </button>
        </div>
      </section>

      <section class="border-b pb-6">
        <h3 class="text-xl font-semibold mb-4">新增教學內容</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm text-gray-600 mb-1">教學標題 (必填)</label>
            <input v-model="newPost.title" type="text" placeholder="輸入標題..." class="border border-gray-300 p-2 w-full rounded focus:ring-blue-500 focus:border-blue-500">
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">內容說明</label>
            <textarea v-model="newPost.description" placeholder="簡單描述一下這個教學..." class="border border-gray-300 p-2 w-full rounded focus:ring-blue-500 focus:border-blue-500 rows-3"></textarea>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">超連結網址 (必填)</label>
            <input v-model="newPost.url" type="url" placeholder="https://..." class="border border-gray-300 p-2 w-full rounded focus:ring-blue-500 focus:border-blue-500">
          </div>
          <button @click="addPost" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition duration-200">
            發布內容
          </button>
        </div>
      </section>

      <section class="border-b pb-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-semibold">外部網站保活與捷徑設定</h3>
          <button 
            @click="pingAllUrls" 
            :disabled="isPinging || keepAliveUrls.length === 0"
            class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50 transition duration-200 flex items-center gap-2 shadow-sm"
          >
            <span>{{ isPinging ? '喚醒中...' : '一鍵喚醒全部' }}</span>
          </button>
        </div>
        
        <p v-if="pingResult" class="text-green-600 text-sm mb-3 font-medium">{{ pingResult }}</p>

        <div class="flex flex-col md:flex-row gap-2 mb-4 bg-gray-50 p-3 rounded-lg border border-gray-200">
          <input v-model="newKeepAlive.name" type="text" placeholder="網站名稱 (必填)" class="border border-gray-300 p-2 md:w-1/4 rounded text-sm focus:ring-blue-500">
          <input v-model="newKeepAlive.url" type="url" placeholder="喚醒 API 網址 (必填)" class="border border-gray-300 p-2 flex-1 rounded text-sm focus:ring-blue-500">
          <input v-model="newKeepAlive.home_url" type="url" placeholder="真正首頁網址 (選填)" class="border border-gray-300 p-2 flex-1 rounded text-sm focus:ring-blue-500">
          <button @click="addKeepAliveUrl" class="bg-gray-800 text-white px-5 py-2 rounded hover:bg-gray-900 text-sm font-medium whitespace-nowrap transition-colors">
            新增網站
          </button>
        </div>

        <ul class="space-y-3">
          <li v-for="item in keepAliveUrls" :key="item.id" class="flex flex-col md:flex-row justify-between md:items-center bg-white p-3 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex flex-col mb-2 md:mb-0">
              <span class="font-bold text-gray-800 text-lg">{{ item.name }}</span>
              <div class="flex flex-col md:flex-row md:items-center gap-2 mt-1">
                <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded truncate max-w-xs md:max-w-md" title="喚醒用 API">
                  ⚡ API: {{ item.url }}
                </span>
                <a v-if="item.home_url" :href="item.home_url" target="_blank" class="inline-flex items-center justify-center text-xs font-bold text-blue-700 bg-blue-100 hover:bg-blue-200 px-3 py-1 rounded-md transition-colors w-fit">
                  🔗 開啟首頁
                </a>
              </div>
            </div>
            <button @click="deleteKeepAliveUrl(item.id)" class="text-red-500 hover:text-white hover:bg-red-500 border border-transparent hover:border-red-600 text-sm px-3 py-1 rounded transition-colors self-end md:self-auto mt-2 md:mt-0">
              刪除
            </button>
          </li>
          <li v-if="keepAliveUrls.length === 0" class="text-sm text-gray-500 text-center py-6 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            尚未加入任何網站，請在上方輸入框新增。
          </li>
        </ul>
      </section>

      <section>
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-semibold">本站來訪紀錄</h3>
          <button @click="loadVisitorLogs" class="text-sm text-blue-600 hover:text-blue-800 underline">
            重新整理
          </button>
        </div>
        <div class="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
          <table class="min-w-full bg-white text-sm text-left">
            <thead class="bg-gray-100 border-b">
              <tr>
                <th class="p-3 font-medium text-gray-700 w-1/4">時間</th>
                <th class="p-3 font-medium text-gray-700 w-1/4">IP 位址</th>
                <th class="p-3 font-medium text-gray-700 w-1/2">設備 (User-Agent)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in visitorLogs" :key="log.id" class="border-b hover:bg-gray-50">
                <td class="p-3 whitespace-nowrap text-gray-600">{{ formatDate(log.visited_at) }}</td>
                <td class="p-3 text-blue-600 font-mono">{{ log.ip_address }}</td>
                <td class="p-3 text-gray-600 truncate max-w-xs" :title="log.user_agent">{{ log.user_agent }}</td>
              </tr>
              <tr v-if="visitorLogs.length === 0">
                <td colspan="3" class="p-5 text-center text-gray-500">目前尚無來訪紀錄</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getTodayPassword } from '@/utils/auth'

const dayjs = useDayjs()
const supabase = useSupabaseClient()

// ====== 狀態變數 ======
const isAuthenticated = ref(false)
const inputPassword = ref('')
const errorMsg = ref('')

const siteTitle = ref('')
const marqueeText = ref('')
const newPost = ref({ title: '', description: '', url: '' })
const visitorLogs = ref([])

// 保活功能與捷徑變數 (加入 home_url)
const keepAliveUrls = ref([])
const newKeepAlive = ref({ name: '', url: '', home_url: '' })
const isPinging = ref(false)
const pingResult = ref('')

// ====== 核心功能 ======

const login = () => {
  const correctPassword = getTodayPassword()
  if (inputPassword.value === correctPassword) {
    isAuthenticated.value = true
    errorMsg.value = ''
    loadSettings()
    loadVisitorLogs()
    loadKeepAliveUrls() // 登入後自動載入保活清單
  } else {
    errorMsg.value = '密碼錯誤！'
  }
}

// 網站設定與發布邏輯
const loadSettings = async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  if (data) {
    siteTitle.value = data.title
    marqueeText.value = data.marquee_text
  }
}

const updateSettings = async () => {
  if (!siteTitle.value || !marqueeText.value) return alert('網站名稱與跑馬燈內容不可為空！')
  await supabase.from('site_settings').upsert({ id: 1, title: siteTitle.value, marquee_text: marqueeText.value })
  alert('設定已更新！')
}

const addPost = async () => {
  if (!newPost.value.title || !newPost.value.url) return alert('「教學標題」與「超連結網址」為必填欄位！')
  await supabase.from('bulletins').insert([{ ...newPost.value }])
  alert('發布成功！')
  newPost.value = { title: '', description: '', url: '' }
}

const loadVisitorLogs = async () => {
  const { data } = await supabase.from('visitor_logs').select('*').order('visited_at', { ascending: false }).limit(10)
  if (data) visitorLogs.value = data
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return dayjs(dateString).format('YYYY/MM/DD HH:mm:ss')
}

// ====== 保活與捷徑功能邏輯 ======

// 載入清單
const loadKeepAliveUrls = async () => {
  const { data } = await supabase.from('keep_alive_urls').select('*').order('created_at', { ascending: false })
  if (data) keepAliveUrls.value = data
}

// 新增網址
const addKeepAliveUrl = async () => {
  if (!newKeepAlive.value.name || !newKeepAlive.value.url) return alert('名稱與喚醒 API 網址為必填！')
  try {
    new URL(newKeepAlive.value.url) // 驗證喚醒網址格式
    if (newKeepAlive.value.home_url) {
      new URL(newKeepAlive.value.home_url) // 如果有填首頁網址，也要驗證格式
    }
  } catch (e) {
    return alert('請輸入有效的網址 (需包含 http:// 或 https://)')
  }
  
  await supabase.from('keep_alive_urls').insert([{ ...newKeepAlive.value }])
  newKeepAlive.value = { name: '', url: '', home_url: '' }
  loadKeepAliveUrls()
}

// 刪除網址
const deleteKeepAliveUrl = async (id) => {
  if (!confirm('確定要刪除這個網站設定嗎？')) return
  await supabase.from('keep_alive_urls').delete().eq('id', id)
  loadKeepAliveUrls()
}

// 一鍵喚醒邏輯
const pingAllUrls = async () => {
  if (keepAliveUrls.value.length === 0) return
  isPinging.value = true
  pingResult.value = ''
  
  let successCount = 0

  // 平行發送請求
  await Promise.allSettled(keepAliveUrls.value.map(async (item) => {
    try {
      const urlObj = new URL(item.url)
      // 加上隨機時間戳，確保繞過 Vercel CDN 快取，強制觸發伺服器與資料庫讀取
      urlObj.searchParams.append('_ping_ts', Date.now().toString())
      
      // 使用 no-cors 模式，即使對方沒有設 CORS headers 也能成功把請求發出去
      await fetch(urlObj.toString(), { 
        method: 'GET',
        mode: 'no-cors', 
        cache: 'no-store' 
      })
      successCount++
    } catch (error) {
      console.error(`喚醒 ${item.name} 失敗:`, error)
    }
  }))

  isPinging.value = false
  pingResult.value = `喚醒完成！成功發送 ${successCount}/${keepAliveUrls.value.length} 個請求。`
  
  // 3秒後清除提示
  setTimeout(() => {
    pingResult.value = ''
  }, 3000)
}
</script>