<template>
  <div class="space-y-8">
    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 class="text-xl font-semibold mb-4 text-gray-800">⚙️ 網站全域設定</h3>
      <div class="space-y-3">
        <div class="flex flex-col md:flex-row gap-3">
          <div class="flex-1">
            <label class="block text-sm text-gray-600 mb-1">網站名稱</label>
            <input v-model="siteTitle" type="text" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
          </div>
          <div class="md:w-1/4">
            <label class="block text-sm text-gray-600 mb-1">網站風格主題</label>
            <select v-model="siteTheme" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent bg-white', themeObj.ring]">
              <option v-for="(config, key) in themeConfig" :key="key" :value="key">{{ config.label }}</option>
            </select>
          </div>
          <div class="md:w-1/4">
            <label class="block text-sm text-gray-600 mb-1">前台公告排序</label>
            <select v-model="siteSortOrder" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent bg-white', themeObj.ring]">
              <option value="newest">🕒 最新公告在前</option>
              <option value="oldest">🕰️ 最舊公告在前</option>
            </select>
          </div>
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">跑馬燈內容</label>
          <input v-model="marqueeText" type="text" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
        </div>
        <button @click="updateSettings" :class="[themeObj.bg, themeObj.hover, 'text-white px-6 py-2 rounded font-medium transition duration-300 shadow-sm']">儲存全域設定</button>
      </div>
    </section>

    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 class="text-xl font-semibold mb-4 flex items-center gap-2">
        🏷️ 前台入口分類管理
        <span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded shadow-sm border border-gray-200">控制前台的科目頁籤</span>
      </h3>
      <div class="flex flex-wrap items-center gap-3 bg-gray-50 p-3 rounded-lg border border-gray-200 min-h-[56px]">
        <div v-for="cat in postCategories" :key="cat.id" class="relative group flex items-center">
          <div v-if="editingCatId === cat.id" class="flex items-center bg-white border-2 border-blue-400 rounded-full px-2 py-1 shadow-sm">
            <input v-model="editingCatIcon" class="w-8 text-sm outline-none px-1 text-center" placeholder="圖示">
            <input v-model="editingCatName" @keyup.enter="saveCatName(cat)" class="w-20 text-sm outline-none px-1" placeholder="名稱">
            <button @click="saveCatName(cat)" class="text-green-600 hover:bg-green-100 p-1 rounded-full text-xs">✔</button>
            <button @click="editingCatId = null" class="text-red-500 hover:bg-red-100 p-1 rounded-full text-xs">✖</button>
          </div>
          <div v-else class="bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-full font-bold text-sm flex items-center gap-1.5 cursor-default shadow-sm hover:bg-gray-100 transition-colors">
            <span>{{ cat.icon }}</span> {{ cat.name }}
            <span @click="startEditCat(cat)" class="text-[10px] opacity-0 group-hover:opacity-100 hover:text-blue-500 transition-opacity ml-1 bg-black/10 px-1.5 py-0.5 rounded cursor-pointer">✎</span>
            <span @click="deleteCategory(cat.id)" class="text-[10px] opacity-0 group-hover:opacity-100 hover:text-red-500 transition-opacity bg-black/10 px-1.5 py-0.5 rounded cursor-pointer">✖</span>
          </div>
        </div>
        <div class="flex items-center ml-auto bg-white border border-gray-300 rounded-full overflow-hidden shadow-sm">
          <input v-model="newCatIcon" type="text" placeholder="圖示(💻)" class="text-sm px-2 py-2 w-20 focus:outline-none border-r border-gray-200 text-center">
          <input v-model="newCatName" type="text" placeholder="+ 新增名稱" class="text-sm px-3 py-2 w-28 md:w-32 focus:outline-none" @keyup.enter="addCategory">
          <button @click="addCategory" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 text-sm font-bold transition-colors border-l border-gray-300">新增</button>
        </div>
      </div>
    </section>

    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 relative">
      <div v-if="showRenderToast" class="absolute top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-10 animate-fade-in flex items-center gap-2">
        <span>🛸</span> 喚醒倒數完成！
      </div>

      <div class="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-3">
        <h3 class="text-xl font-semibold text-gray-800">🚀 外部網站保活與捷徑設定</h3>
        <div class="flex gap-2">
          <button @click="pingUrlsByPlatform('Vercel')" :disabled="isPinging" class="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-900 disabled:opacity-50 transition duration-300 flex items-center shadow-sm text-sm">
            <span v-if="isPingingPlatform === 'Vercel'" class="animate-pulse">⏳ 喚醒中...</span>
            <span v-else>🚀 喚醒 Vercel</span>
          </button>
          <button @click="pingUrlsByPlatform('Render')" :disabled="isPinging" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50 transition duration-300 flex items-center shadow-sm text-sm">
            <span v-if="isPingingPlatform === 'Render'" class="animate-pulse">⏳ 喚醒中...</span>
            <span v-else>🛸 喚醒 Render</span>
          </button>
        </div>
      </div>
      
      <p v-if="pingResult" :class="[themeObj.text, 'text-sm mb-3 font-bold']">{{ pingResult }}</p>

      <div class="flex flex-col md:flex-row gap-2 mb-6 bg-gray-50 p-3 rounded-lg border border-gray-200">
        <select v-model="newKeepAlive.platform" :class="['border border-gray-300 p-2 rounded text-sm bg-white focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
          <option value="Vercel">Vercel</option><option value="Render">Render</option>
        </select>
        <input v-model="newKeepAlive.name" type="text" placeholder="名稱" :class="['border border-gray-300 p-2 w-full md:w-32 rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
        <input v-model="newKeepAlive.url" type="url" placeholder="喚醒 API" :class="['border border-gray-300 p-2 flex-1 rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
        <input v-model="newKeepAlive.home_url" type="url" placeholder="首頁網址" :class="['border border-gray-300 p-2 flex-1 rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
        <button @click="addKeepAliveUrl" :class="[themeObj.bg, themeObj.hover, 'text-white px-5 py-2 rounded text-sm font-medium shadow-sm']">新增</button>
      </div>

      <div class="space-y-6">
        <div>
          <h4 class="text-sm font-bold text-gray-500 mb-2">▲ Vercel 專案</h4>
          <ul class="space-y-2">
            <li v-for="item in vercelUrls" :key="item.id" class="flex flex-col md:flex-row justify-between md:items-center bg-white p-3 rounded border-l-4 border-l-gray-800 shadow-sm border border-gray-200">
              <div class="flex flex-col mb-2 md:mb-0">
                <span class="font-bold text-gray-800">{{ item.name }}</span>
                <div class="flex flex-col md:flex-row md:items-center gap-2 mt-1">
                  <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded truncate max-w-xs md:max-w-md">⚡ API: {{ item.url }}</span>
                  <a v-if="item.home_url" :href="item.home_url" target="_blank" :class="['inline-flex items-center justify-center text-xs font-bold bg-opacity-10 hover:bg-opacity-20 px-3 py-1 rounded-md w-fit', themeObj.text, themeObj.bg.replace('bg-', 'bg-').replace('600', '100')]">🔗 開啟首頁</a>
                </div>
              </div>
              <button @click="deleteKeepAliveUrl(item.id)" class="text-red-500 text-sm hover:underline self-end md:self-auto">刪除</button>
            </li>
          </ul>
        </div>
        <div>
          <h4 class="text-sm font-bold text-purple-500 mb-2">◆ Render 專案</h4>
          <ul class="space-y-2">
            <li v-for="item in renderUrls" :key="item.id" class="flex flex-col md:flex-row justify-between md:items-center bg-white p-3 rounded border-l-4 border-l-purple-500 shadow-sm border border-gray-200">
              <div class="flex flex-col mb-2 md:mb-0">
                <span class="font-bold text-gray-800">{{ item.name }}</span>
                <div class="flex flex-col md:flex-row md:items-center gap-2 mt-1">
                  <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded truncate max-w-xs md:max-w-md">⚡ API: {{ item.url }}</span>
                  <a v-if="item.home_url" :href="item.home_url" target="_blank" :class="['inline-flex items-center justify-center text-xs font-bold bg-opacity-10 hover:bg-opacity-20 px-3 py-1 rounded-md w-fit', themeObj.text, themeObj.bg.replace('bg-', 'bg-').replace('600', '100')]">🔗 開啟首頁</a>
                </div>
              </div>
              <button @click="deleteKeepAliveUrl(item.id)" class="text-red-500 text-sm hover:underline self-end md:self-auto">刪除</button>
            </li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { themeConfig } from '@/utils/theme'
const supabase = useSupabaseClient()
const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const siteTitle = ref(''); const marqueeText = ref(''); const siteTheme = ref('purple'); const siteSortOrder = ref('newest')
const postCategories = ref([]); const newCatName = ref(''); const newCatIcon = ref(''); const editingCatId = ref(null); const editingCatName = ref(''); const editingCatIcon = ref('')
const keepAliveUrls = ref([]); const newKeepAlive = ref({ name: '', url: '', home_url: '', platform: 'Vercel' }); const isPinging = ref(false); const isPingingPlatform = ref(''); const pingResult = ref('')
const showRenderToast = ref(false)
const vercelUrls = computed(() => keepAliveUrls.value.filter(item => item.platform === 'Vercel' || !item.platform))
const renderUrls = computed(() => keepAliveUrls.value.filter(item => item.platform === 'Render'))

onMounted(() => {
  loadSettings(); loadPostCategories(); loadKeepAliveUrls()
})

const loadSettings = async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  if (data) { siteTitle.value = data.title; marqueeText.value = data.marquee_text; siteTheme.value = data.theme || 'purple'; siteSortOrder.value = data.sort_order || 'newest'; currentTheme.value = siteTheme.value }
}
const updateSettings = async () => {
  if (!siteTitle.value || !marqueeText.value) return alert('名稱與跑馬燈必填！')
  await supabase.from('site_settings').upsert({ id: 1, title: siteTitle.value, marquee_text: marqueeText.value, theme: siteTheme.value, sort_order: siteSortOrder.value })
  currentTheme.value = siteTheme.value; alert('設定已更新！')
}

const loadPostCategories = async () => {
  const { data } = await supabase.from('post_categories').select('*').order('id', { ascending: true })
  if (data) postCategories.value = data
}
const addCategory = async () => {
  if (!newCatName.value) return alert('分類名稱不可為空！')
  await supabase.from('post_categories').insert([{ name: newCatName.value, icon: newCatIcon.value || '📌' }]); newCatName.value = ''; newCatIcon.value = ''; loadPostCategories()
}
const deleteCategory = async (id) => {
  if (!confirm('確定要刪除嗎？')) return
  await supabase.from('post_categories').delete().eq('id', id); loadPostCategories()
}
const startEditCat = (cat) => { editingCatId.value = cat.id; editingCatName.value = cat.name; editingCatIcon.value = cat.icon }
const saveCatName = async (cat) => {
  if (!editingCatName.value) return alert('名稱不可為空！')
  await supabase.from('post_categories').update({ name: editingCatName.value, icon: editingCatIcon.value }).eq('id', cat.id); editingCatId.value = null; loadPostCategories()
}

const loadKeepAliveUrls = async () => {
  const { data } = await supabase.from('keep_alive_urls').select('*').order('created_at', { ascending: false }); if (data) keepAliveUrls.value = data
}
const addKeepAliveUrl = async () => {
  if (!newKeepAlive.value.name || !newKeepAlive.value.url) return alert('必填！')
  await supabase.from('keep_alive_urls').insert([{ ...newKeepAlive.value }]); newKeepAlive.value = { name: '', url: '', home_url: '', platform: 'Vercel' }; loadKeepAliveUrls()
}
const deleteKeepAliveUrl = async (id) => {
  if (confirm('確定刪除？')) { await supabase.from('keep_alive_urls').delete().eq('id', id); loadKeepAliveUrls() }
}
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))
const pingUrlsByPlatform = async (platform) => {
  const targetUrls = platform === 'Vercel' ? vercelUrls.value : renderUrls.value
  if (targetUrls.length === 0) return
  isPinging.value = true; isPingingPlatform.value = platform; pingResult.value = ''; let successCount = 0
  for (const item of targetUrls) {
    try { const urlObj = new URL(item.url); urlObj.searchParams.append('_ping_ts', Date.now().toString()); await fetch(urlObj.toString(), { method: 'GET', mode: 'no-cors', cache: 'no-store' }); successCount++; await delay(300) } catch (error) {}
  }
  isPinging.value = false; isPingingPlatform.value = ''; pingResult.value = `${platform} 喚醒完成！成功發送 ${successCount}/${targetUrls.length} 個請求。`; setTimeout(() => { pingResult.value = '' }, 4000)
  if (platform === 'Render') { setTimeout(() => { showRenderToast.value = true; setTimeout(() => { showRenderToast.value = false }, 10000) }, 60000) }
}
</script>
<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>