<template>
  <div>
    <div class="flex justify-center space-x-2 md:space-x-4 mt-6 mb-8">
      <button 
        @click="activeCategory = '資訊科技'"
        :class="activeCategory === '資訊科技' ? [themeObj.bg, 'text-white shadow-md'] : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'"
        class="px-6 py-3 rounded-full font-bold text-sm md:text-base transition-all duration-300 flex items-center gap-2"
      >
        <span>💻</span> 資訊科技入口
      </button>
      
      <button 
        @click="activeCategory = '英語'"
        :class="activeCategory === '英語' ? [themeObj.bg, 'text-white shadow-md'] : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'"
        class="px-6 py-3 rounded-full font-bold text-sm md:text-base transition-all duration-300 flex items-center gap-2"
      >
        <span>🔤</span> 英語學習入口
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

    <div v-else class="text-center py-16 text-gray-400">
      <div class="text-4xl mb-3">📭</div>
      <p>目前這個科目還沒有教學內容喔！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { themeConfig } from '@/utils/theme'

const supabase = useSupabaseClient()
const dayjs = useDayjs()
const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const activeCategory = ref('資訊科技')

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

// 時間格式化
const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY/MM/DD HH:mm')
}

// 過濾與動態排序邏輯
const filteredBulletins = computed(() => {
  if (!bulletins.value) return []
  let filtered = bulletins.value.filter(b => b.category === activeCategory.value)
  
  return filtered.sort((a, b) => {
    // 📌 規則 1: 置頂永遠最優先
    if (a.is_pinned !== b.is_pinned) {
      return a.is_pinned ? -1 : 1 
    }
    
    // 🕒 規則 2: 依照後台設定的時間排序
    const dateA = new Date(a.created_at).getTime()
    const dateB = new Date(b.created_at).getTime()
    
    if (sortOrder.value === 'oldest') {
      return dateA - dateB // 最舊在前
    } else {
      return dateB - dateA // 最新在前 (預設)
    }
  })
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>