<template>
  <div class="space-y-8">
    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 class="text-xl font-semibold mb-4 text-gray-800">⚙️ 網站全域設定</h3>
      <div class="space-y-3">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <div class="md:col-span-1">
            <label class="block text-sm text-gray-600 mb-1">網站名稱</label>
            <input v-model="siteTitle" type="text" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">網站風格主題</label>
            <select v-model="siteTheme" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent bg-white', themeObj.ring]">
              <option v-for="(config, key) in themeConfig" :key="key" :value="key">{{ config.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">前台公告排序</label>
            <select v-model="siteSortOrder" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent bg-white', themeObj.ring]">
              <option value="newest">🕒 最新公告在前</option>
              <option value="oldest">🕰️ 最舊公告在前</option>
            </select>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">編輯器進入密碼</label>
            <input v-model="editorPassword" type="text" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]" placeholder="預設 590doc">
          </div>
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">跑馬燈內容</label>
          <input v-model="marqueeText" type="text" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
        </div>
        <button @click="updateSettings" :class="[themeObj.bg, themeObj.hover, 'text-white px-6 py-2 rounded font-medium transition duration-300 shadow-sm']">儲存全域設定</button>
      </div>
    </section>

    <section class="mt-8 bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex flex-col max-h-[500px]">
      <div class="bg-gray-50 px-5 py-4 border-b border-gray-200 flex justify-between items-center">
        <h3 class="font-bold text-gray-700">🕵️‍♂️ 近期網站來訪者紀錄</h3>
        <button @click="fetchVisitorLogs" class="text-xs bg-white border border-gray-300 text-gray-600 px-3 py-1.5 rounded hover:bg-gray-100 shadow-sm transition-colors flex items-center gap-1">
          <span>🔄</span> 重新整理
        </button>
      </div>
      <div class="overflow-x-auto overflow-y-auto flex-1 p-0">
        <table class="w-full text-left text-sm text-gray-600">
          <thead class="bg-white sticky top-0 shadow-sm z-10">
            <tr>
              <th class="px-5 py-3 font-semibold text-gray-800 whitespace-nowrap">造訪時間</th>
              <th class="px-5 py-3 font-semibold text-gray-800 whitespace-nowrap">IP 位址</th>
              <th class="px-5 py-3 font-semibold text-gray-800">設備 / 瀏覽器特徵 (User Agent)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="log in visitorLogs" :key="log.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-5 py-3 whitespace-nowrap font-mono text-xs">{{ formatDate(log.visited_at) }}</td>
              <td class="px-5 py-3 font-mono text-xs text-blue-600 font-bold">{{ log.ip_address || '未知 IP' }}</td>
              <td class="px-5 py-3 text-xs text-gray-500 break-all">{{ log.user_agent || '未知設備' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { themeConfig } from '@/utils/theme'
const supabase = useSupabaseClient()
const dayjs = useDayjs()
const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const siteTitle = ref(''); const marqueeText = ref(''); const siteTheme = ref('purple'); const siteSortOrder = ref('newest');
const editorPassword = ref('590doc') // 🌟 新增狀態

// (其餘分類與保活邏輯的 ref 省略...)

onMounted(() => {
  loadSettings();
  // ... 其他載入邏輯
})

const loadSettings = async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  if (data) {
    siteTitle.value = data.title;
    marqueeText.value = data.marquee_text;
    siteTheme.value = data.theme || 'purple';
    siteSortOrder.value = data.sort_order || 'newest';
    editorPassword.value = data.editor_password || '590doc'; // 🌟 讀取密碼
    currentTheme.value = siteTheme.value
  }
}

const updateSettings = async () => {
  await supabase.from('site_settings').upsert({
    id: 1,
    title: siteTitle.value,
    marquee_text: marqueeText.value,
    theme: siteTheme.value,
    sort_order: siteSortOrder.value,
    editor_password: editorPassword.value // 🌟 存入密碼
  })
  currentTheme.value = siteTheme.value;
  alert('設定已更新！')
}

// (其餘功能與 fetchVisitorLogs 保持不變...)
</script>
