<template>
  <div class="min-h-screen bg-gray-50 font-sans">
    <div :class="[themeObj.bg, 'text-white overflow-hidden whitespace-nowrap py-2 px-4 relative transition-colors duration-300']">
      <div class="inline-block animate-marquee">
        📢 {{ settings?.marquee_text || '歡迎來到教學佈告欄...' }}
      </div>
    </div>

    <header class="bg-white shadow-sm p-4 flex justify-between items-center transition-colors duration-300">
      <h1 class="text-2xl font-bold text-gray-800">{{ settings?.title || '教學佈告欄' }}</h1>
      <NuxtLink to="/admin" :class="['text-sm font-bold hover:opacity-75 transition-colors', themeObj.text]">管理後台</NuxtLink>
    </header>

    <main class="container mx-auto p-4 max-w-4xl">
      <NuxtPage />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { themeConfig } from '@/utils/theme'

const supabase = useSupabaseClient()

// 建立全域響應式主題狀態，預設為 purple
const currentTheme = useState('currentTheme', () => 'purple')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const { data: settings } = await useAsyncData('settings', async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  if (data?.theme) currentTheme.value = data.theme // 從資料庫讀取主題
  return data
})

onMounted(() => {
  $fetch('/api/log-visitor', { method: 'POST' }).catch(() => {})
})
</script>

<style>
@keyframes marquee {
  0% { transform: translateX(100vw); }
  100% { transform: translateX(-100%); }
}
.animate-marquee { animation: marquee 15s linear infinite; }
</style>