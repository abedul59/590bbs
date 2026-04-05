<template>
  <div>
    <div class="flex justify-center space-x-2 md:space-x-4 mt-6 mb-6 flex-wrap gap-y-3">
      <button 
        v-for="cat in categories" :key="cat.id"
        @click="activeCategory = cat.name"
        :class="activeCategory === cat.name ? [themeObj.bg, 'text-white shadow-md'] : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'"
        class="px-5 py-2.5 md:px-6 md:py-3 rounded-full font-bold text-sm md:text-base transition-all duration-300 flex items-center gap-2"
      >
        <span>{{ cat.icon }}</span> {{ cat.name }}
      </button>
      <div v-if="categories.length === 0" class="text-sm text-gray-400">目前尚無分類，請至後台新增。</div>
    </div>

    <div class="mb-8 max-w-2xl mx-auto bg-blue-50 border border-blue-200 p-4 md:p-6 rounded-2xl shadow-sm text-center flex flex-col items-center justify-center animate-fade-in">
      <h4 class="font-bold text-blue-900 mb-2 text-lg">📅 每日學習打卡</h4>
      <p class="text-sm text-blue-600 mb-4">記錄你的每一天，保持學習好習慣！</p>
      
      <button 
        @click="handleStudentCheckIn" 
        :disabled="hasCheckedIn"
        class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-10 rounded-full shadow-md transition-all transform hover:scale-105 disabled:opacity-80 disabled:hover:scale-100 disabled:cursor-not-allowed flex items-center gap-2"
      >
        <span>{{ hasCheckedIn ? '✅ 你今日已成功打卡' : '✋ 點我進行學生簽到' }}</span>
      </button>
    </div>

    <div v-if="filteredBulletins.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
      <div 
        v-for="item in filteredBulletins" 
        :key="item.id" 
        :class="[
          'relative p-6 rounded-xl shadow-sm hover:shadow-md transition duration-300 group flex flex-col h-full',
          item.is_important ? `bg-red-50 border-2 border-red-400` : 'bg-white border border-gray-200'
        ]"
      >
        <div class="absolute -top-3 -right-2 flex gap-1">
          <span v-if="item.is_pinned" class="bg-yellow-400 text-white text-xs font-bold px-2 py-1 rounded-full shadow">📌 置頂</span>
          <span v-if="item.is_important" class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow">🔥 重要</span>
        </div>

        <div class="flex-1">
          <div class="text-xs text-gray-400 mb-2 flex items-center gap-1 font-mono">
            🕒 {{ formatDate(item.created_at) }}
          </div>
          
          <h5 :class="['text-xl font-bold tracking-tight transition-colors duration-300 mb-2 pr-10', item.is_important ? 'text-red-700' : 'text-gray-900', themeObj.hoverText]">
            {{ item.title }}
          </h5>
          <p class="font-normal text-gray-600 whitespace-pre-line">{{ item.description }}</p>
        </div>

        <div class="mt-5 flex flex-wrap gap-2">
          <a :href="item.url" target="_blank" :class="[themeObj.bg, themeObj.hover, 'text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm transition-colors']">
            前往主連結 🚀
          </a>
          <a 
            v-for="(link, index) in item.links || []" 
            :key="index"
            :href="link.url" 
            target="_blank"
            class="bg-white border border-gray-300 text-gray-700 hover:bg-gray-100 px-4 py-2 rounded-lg text-sm font-bold shadow-sm transition-colors"
          >
            {{ link.name || '參考網址' }}
          </a>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-16 text-gray-400 animate-fade-in">
      <div class="text-4xl mb-3">📭</div>
      <p>目前這個科目還沒有教學內容喔！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { themeConfig } from '@/utils/theme'

const supabase = useSupabaseClient()
const dayjs = useDayjs()
const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const activeCategory = ref('')

// ====== 🌟 學生打卡與後台保活喚醒邏輯 ======
const hasCheckedIn = ref(false)

// 填入所有您想要「順便喚醒」的 API 網址 (包含 Hugging Face 與 Render)
const serversToWakeUp = [
  'https://lawxstudents168-tg-material-api.hf.space',
  'https://lawxstudents168-tg-uploader-api.hf.space',
  'https://lawxstudents168-tg-uploader-api-grjhs.hf.space'
  // 如果還有 Render 的網址也可以加在這邊
]

const handleStudentCheckIn = async () => {
  if (hasCheckedIn.value) return
  
  // 1. 表面功夫：給學生的即時開心回饋
  alert('🎉 你今日成功打卡了！繼續保持喔！')
  hasCheckedIn.value = true

  try {
    // 2. 核心保活 1：寫入紀錄到 Supabase (防止資料庫因 7 天無活動被暫停)
    await supabase.from('system_keepalive_logs').insert([
      { action_type: 'student_checkin' }
    ])

    // 3. 核心保活 2：背景並發請求，喚醒所有沉睡的伺服器
    serversToWakeUp.forEach(url => {
      fetch(`${url}/?_ping=${Date.now()}`, { 
        method: 'GET', 
        mode: 'no-cors',
        cache: 'no-store' // 強制不使用快取
      }).catch(() => {}) // 忽略錯誤，我們只負責戳醒它
    })

  } catch (error) {
    console.error('背景喚醒作業發生小錯誤，但不影響前端打卡', error)
  }
}
// ==========================================

// 取得前台動態分類
const { data: categories } = await useAsyncData('categories', async () => {
  const { data } = await supabase.from('post_categories').select('*').order('id', { ascending: true })
  return data || []
})

// 預設選擇第一個分類
if (categories.value && categories.value.length > 0) {
  activeCategory.value = categories.value[0].name
}

// 取得網站全域設定 (包含排序方式)
const { data: settings } = await useAsyncData('site_settings', async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  return data
})
const sortOrder = computed(() => settings.value?.sort_order || 'newest')

// 取得公告資料
const { data: bulletins } = await useAsyncData('bulletins', async () => {
  const { data } = await supabase.from('bulletins').select('*')
  return data
})

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY/MM/DD HH:mm')
}

// 過濾與動態排序邏輯
const filteredBulletins = computed(() => {
  if (!bulletins.value) return []
  let filtered = bulletins.value.filter(b => b.category === activeCategory.value)
  
  return filtered.sort((a, b) => {
    if (a.is_pinned !== b.is_pinned) {
      return a.is_pinned ? -1 : 1 
    }
    const dateA = new Date(a.created_at).getTime()
    const dateB = new Date(b.created_at).getTime()
    
    if (sortOrder.value === 'oldest') {
      return dateA - dateB
    } else {
      return dateB - dateA
    }
  })
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
