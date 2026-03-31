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
      <a 
        v-for="item in filteredBulletins" 
        :key="item.id" 
        :href="item.url" 
        target="_blank"
        :class="['block p-6 bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition duration-300 group hover:border-transparent']"
      >
        <div class="flex justify-between items-start mb-2">
          <h5 :class="['text-xl font-bold tracking-tight text-gray-900 transition-colors duration-300', themeObj.hoverText]">{{ item.title }}</h5>
        </div>
        <p class="font-normal text-gray-600 mt-2">{{ item.description }}</p>
        <div :class="['mt-4 text-sm font-medium flex items-center gap-1 transition-transform group-hover:translate-x-1 duration-300', themeObj.text]">
          點擊前往學習 <span aria-hidden="true">&rarr;</span>
        </div>
      </a>
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
const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const activeCategory = ref('資訊科技')

const { data: bulletins } = await useAsyncData('bulletins', async () => {
  const { data } = await supabase.from('bulletins').select('*').order('created_at', { ascending: false })
  return data
})

const filteredBulletins = computed(() => {
  if (!bulletins.value) return []
  return bulletins.value.filter(b => b.category === activeCategory.value)
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>