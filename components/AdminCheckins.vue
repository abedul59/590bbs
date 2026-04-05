<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex justify-between items-center border-b border-gray-200 pb-3">
      <h2 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
        <span>📅</span> 學生打卡與保活喚醒紀錄
      </h2>
      <button @click="fetchLogs" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 px-4 py-2 rounded-lg text-sm font-bold transition-colors flex items-center gap-2 shadow-sm">
        <span :class="{'animate-spin': isFetching}">🔄</span> 重新整理
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-md relative overflow-hidden">
        <div class="absolute top-0 right-0 -mt-4 -mr-4 text-white opacity-20 text-8xl">🔥</div>
        <h3 class="text-blue-100 text-sm font-bold mb-1 relative z-10">今日打卡次數</h3>
        <p class="text-4xl font-extrabold relative z-10">{{ todayCount }} <span class="text-lg font-medium">次</span></p>
      </div>
      <div class="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-xl p-6 text-white shadow-md relative overflow-hidden">
        <div class="absolute top-0 right-0 -mt-4 -mr-4 text-white opacity-20 text-8xl">📈</div>
        <h3 class="text-indigo-100 text-sm font-bold mb-1 relative z-10">總計喚醒次數</h3>
        <p class="text-4xl font-extrabold relative z-10">{{ totalCount }} <span class="text-lg font-medium">次</span></p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex flex-col max-h-[500px]">
        <div class="bg-gray-50 px-5 py-4 border-b border-gray-200">
          <h3 class="font-bold text-gray-700">📊 每日打卡統計 (近期)</h3>
        </div>
        <div class="overflow-y-auto flex-1 p-0">
          <table class="w-full text-left text-sm text-gray-600">
            <thead class="bg-white sticky top-0 shadow-sm z-10">
              <tr>
                <th class="px-5 py-3 font-semibold text-gray-800">打卡日期</th>
                <th class="px-5 py-3 font-semibold text-gray-800 text-right">貢獻次數</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="stat in dailyStats" :key="stat.date" class="hover:bg-gray-50 transition-colors">
                <td class="px-5 py-3 font-mono font-medium">{{ stat.date }}</td>
                <td class="px-5 py-3 text-right">
                  <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-bold text-xs shadow-sm">
                    {{ stat.count }} 次
                  </span>
                </td>
              </tr>
              <tr v-if="dailyStats.length === 0">
                <td colspan="2" class="px-5 py-10 text-center text-gray-400">尚無打卡紀錄</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex flex-col max-h-[500px]">
        <div class="bg-gray-50 px-5 py-4 border-b border-gray-200">
          <h3 class="font-bold text-gray-700">🕒 最新打卡時間 (最近 100 筆)</h3>
        </div>
        <ul class="overflow-y-auto flex-1 divide-y divide-gray-100 p-2">
          <li v-for="log in recentLogs" :key="log.id" class="px-4 py-3 flex items-center justify-between hover:bg-gray-50 rounded-lg my-1 transition-colors">
            <div class="flex items-center gap-3">
              <span class="text-2xl bg-gray-100 p-2 rounded-full">👤</span>
              <div>
                <p class="text-sm font-bold text-gray-800">熱心學生打卡</p>
                <p class="text-xs text-gray-500 font-mono mt-0.5">{{ formatDate(log.created_at) }}</p>
              </div>
            </div>
            <span class="text-xs text-green-700 bg-green-100 border border-green-200 px-2 py-1.5 rounded-md font-bold shadow-sm flex items-center gap-1">
              <span>🚀</span> 喚醒成功
            </span>
          </li>
          <li v-if="recentLogs.length === 0" class="px-4 py-10 text-center text-gray-400">
            尚無詳細紀錄
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
const supabase = useSupabaseClient()
const dayjs = useDayjs()

const rawLogs = ref([])
const isFetching = ref(false)

const fetchLogs = async () => {
  isFetching.value = true
  // 抓取最近的紀錄來做統計 (限制 2000 筆避免過載)
  const { data, error } = await supabase
    .from('system_keepalive_logs')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(2000)
    
  if (data) rawLogs.value = data
  setTimeout(() => { isFetching.value = false }, 500)
}

onMounted(() => { fetchLogs() })

// === 工具函式 ===
const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY/MM/DD HH:mm:ss')
}
const formatJustDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD')
}

// === 計算屬性 ===
// 1. 總計次數
const totalCount = computed(() => rawLogs.value.length)

// 2. 今日次數
const todayCount = computed(() => {
  const todayStr = dayjs().format('YYYY-MM-DD')
  return rawLogs.value.filter(log => formatJustDate(log.created_at) === todayStr).length
})

// 3. 每日統計陣列 (彙整)
const dailyStats = computed(() => {
  const stats = {}
  rawLogs.value.forEach(log => {
    const d = formatJustDate(log.created_at)
    if (!stats[d]) stats[d] = 0
    stats[d]++
  })
  // 轉成陣列並按照日期排序(最新的在上面)
  return Object.keys(stats).map(date => ({
    date, count: stats[date]
  })).sort((a, b) => b.date.localeCompare(a.date))
})

// 4. 最近 100 筆紀錄
const recentLogs = computed(() => rawLogs.value.slice(0, 100))
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
