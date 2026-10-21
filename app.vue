<template>
  <div
    :class="['site-shell min-h-screen bg-gray-50 font-sans', { 'festival-site': themeObj.festival && !macrowaveMode, 'macrowave-mode': macrowaveMode }]"
    :style="festivalStyle"
    :data-theme="currentTheme"
  >
    <div v-if="themeObj.festival && !macrowaveMode" class="festival-decor festival-decor-left" aria-hidden="true">{{ themeObj.festival.motifs[0] }}</div>
    <div v-if="themeObj.festival && !macrowaveMode" class="festival-decor festival-decor-right" aria-hidden="true">{{ themeObj.festival.motifs[1] }}</div>

    <div v-if="!macrowaveMode" :class="[themeObj.festival ? 'festival-banner' : themeObj.bg, 'site-marquee text-white overflow-hidden whitespace-nowrap py-2 px-4 relative transition-colors duration-300']">
      <div class="inline-block animate-marquee">
        📢 {{ settings?.marquee_text || '歡迎來到教學佈告欄...' }}
      </div>
    </div>

    <header v-if="!macrowaveMode" class="site-header bg-white shadow-sm p-4 flex justify-between items-center transition-colors duration-300">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">{{ settings?.title || '教學佈告欄' }}</h1>
        <p v-if="themeObj.festival" class="festival-subtitle">{{ themeObj.festival.motifs.join(' ') }} {{ themeObj.festival.description }}</p>
      </div>
      <NuxtLink to="/admin" :class="['text-sm font-bold hover:opacity-75 transition-colors', themeObj.text]">管理後台</NuxtLink>
    </header>

    <main :class="macrowaveMode ? 'site-main w-full max-w-none p-0' : 'site-main container mx-auto p-4 max-w-4xl'">
      <NuxtPage />
    </main>

    <FloatingEditor v-if="!macrowaveMode" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { themeConfig } from '@/utils/theme'

const supabase = useSupabaseClient()

// 建立全域響應式主題狀態，預設為 purple
const currentTheme = useState('currentTheme', () => 'purple')
const macrowaveMode = useState('macrowaveMode', () => false)
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)
const festivalStyle = computed(() => {
  if (macrowaveMode.value) return undefined
  const skin = themeObj.value.festival
  if (!skin) return undefined
  return {
    '--festival-scene': skin.scene,
    '--festival-header': skin.header,
    '--festival-surface': skin.surface,
    '--festival-surface-alt': skin.surfaceAlt,
    '--festival-border': skin.border,
    '--festival-ink': skin.ink,
    '--festival-radius': skin.radius,
    '--festival-shadow': skin.shadow,
    '--festival-font': skin.font,
  }
})

// 載入網站全域設定
const { data: settings } = await useAsyncData('settings', async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  if (data?.theme) currentTheme.value = data.theme // 從資料庫讀取主題
  return data
})

onMounted(() => {
  // 背景自動呼叫來訪者紀錄 API
  $fetch('/api/log-visitor', { method: 'POST' }).catch((err) => {
    console.error('訪客紀錄背景寫入失敗:', err)
  })
})
</script>

<style>
@keyframes marquee {
  0% { transform: translateX(100vw); }
  100% { transform: translateX(-100%); }
}
.animate-marquee { animation: marquee 15s linear infinite; }
.macrowave-mode { background: #f4f6f9 !important; }

.festival-site {
  position: relative;
  overflow-x: hidden;
  background: var(--festival-scene) fixed !important;
  background-size: cover !important;
  color: var(--festival-ink);
  font-family: var(--festival-font);
  transition: background .45s ease, color .3s ease;
}
.festival-site .festival-banner {
  background: var(--festival-header);
  box-shadow: 0 4px 18px color-mix(in srgb, var(--festival-border) 35%, transparent);
  letter-spacing: .04em;
}
.festival-site .site-header {
  position: relative;
  z-index: 2;
  color: var(--festival-ink);
  background: color-mix(in srgb, var(--festival-surface) 90%, transparent) !important;
  border-bottom: 2px solid var(--festival-border);
  backdrop-filter: blur(12px);
}
.festival-site .site-header h1 { color: var(--festival-ink) !important; letter-spacing: .035em; }
.festival-subtitle { margin-top: .2rem; color: var(--festival-ink); font-size: .72rem; opacity: .72; }
.festival-site .site-main { position: relative; z-index: 1; }
.festival-decor {
  position: fixed;
  z-index: 0;
  pointer-events: none;
  user-select: none;
  opacity: .12;
  filter: saturate(.9);
  font-size: clamp(7rem, 18vw, 15rem);
  line-height: 1;
}
.festival-decor-left { left: -2.5rem; top: 18vh; transform: rotate(-13deg); }
.festival-decor-right { right: -2rem; bottom: 3vh; transform: rotate(12deg); }

/* Festival themes restyle every page and admin panel without changing status colors. */
.festival-site main :is(section, .bg-white):not(.bg-red-50) {
  background-color: var(--festival-surface) !important;
  border-color: var(--festival-border) !important;
  border-radius: var(--festival-radius) !important;
  box-shadow: var(--festival-shadow);
  backdrop-filter: blur(8px);
}
.festival-site main :is(.bg-gray-50, .bg-gray-100, .bg-gray-50\/50) {
  background-color: var(--festival-surface-alt) !important;
  border-color: color-mix(in srgb, var(--festival-border) 65%, transparent) !important;
}
.festival-site main :is(.text-gray-900, .text-gray-800, .text-gray-700) { color: var(--festival-ink) !important; }
.festival-site main :is(input, textarea, select) {
  border-color: color-mix(in srgb, var(--festival-border) 70%, #cbd5e1) !important;
  border-radius: var(--festival-radius) !important;
}
.festival-site main :is(.rounded-xl, .rounded-2xl) { border-radius: var(--festival-radius) !important; }
.festival-site main .shadow-sm { box-shadow: 0 6px 18px color-mix(in srgb, var(--festival-border) 18%, transparent); }
.festival-site main a, .festival-site main button { font-family: var(--festival-font); }

@media (max-width: 640px) {
  .festival-decor { opacity: .08; font-size: 7rem; }
  .festival-subtitle { display: none; }
}
</style>
