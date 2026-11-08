<template>
  <div class="space-y-6 animate-fade-in">
    <div class="flex justify-between items-center border-b border-gray-200 pb-3">
      <h2 class="text-2xl font-bold text-gray-800 flex items-center gap-2">
        <span>⏰</span> 自動定時喚醒排程
      </h2>
    </div>

    <div class="bg-indigo-50 border border-indigo-200 p-4 rounded-xl shadow-sm text-indigo-800 text-sm">
      <p class="font-bold mb-1">💡 運作原理：</p>
      <p>cron-job.org 每小時呼叫下方的 Vercel 轉接網址。Vercel 立即回傳 HTTP 204 空內容，再於背景喚醒 Render，避免 Render 冷啟動畫面造成「Response data too big」。Render 恢復後會補處理最近 65 分鐘內尚未記錄的排程。</p>
      <p class="mt-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 font-bold text-red-700">請勿把 cron-job.org 指向 <code>https://five90bbs-render-cron-api.onrender.com/run</code>；該網址會輸出大量執行結果。請將原工作的 URL 改成下方網址。</p>
      <div class="mt-3 flex flex-col gap-2 md:flex-row md:items-center">
        <code class="flex-1 overflow-x-auto rounded-lg border border-indigo-200 bg-white px-3 py-2 text-xs text-indigo-900">{{ cronBridgeUrl }}</code>
        <button type="button" class="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-bold text-white hover:bg-indigo-700" @click="copyCronUrl">複製 cron-job.org 網址</button>
        <button type="button" :disabled="isTesting" class="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-700 disabled:opacity-50" @click="testCronBridge">
          {{ isTesting ? '測試中…' : '立即測試喚醒' }}
        </button>
      </div>
      <p v-if="testMessage" :class="['mt-2 font-bold', testSucceeded ? 'text-emerald-700' : 'text-red-700']">{{ testMessage }}</p>
    </div>

    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div class="flex flex-col md:flex-row gap-3 mb-6 bg-gray-50 p-4 rounded-lg border border-gray-200 items-end">
        <div class="flex-1">
          <label class="block text-sm font-bold text-gray-700 mb-1">設定每日喚醒時間 (台灣時間，24小時制)</label>
          <input v-model="newTime" type="time" class="border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white">
        </div>
        <button @click="addSchedule" class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded font-bold shadow-sm transition-colors">
          + 新增排程
        </button>
      </div>

      <table class="w-full text-left text-sm text-gray-600 border-collapse">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-5 py-3 font-semibold text-gray-800">每日觸發時間</th>
            <th class="px-5 py-3 font-semibold text-gray-800 text-center">狀態</th>
            <th class="px-5 py-3 font-semibold text-gray-800 text-right">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="item in schedules" :key="item.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-5 py-3 font-mono font-bold text-lg text-indigo-700">{{ item.time_str }}</td>
            <td class="px-5 py-3 text-center">
              <button @click="toggleStatus(item)" :class="item.is_active ? 'bg-green-100 text-green-700 border-green-200' : 'bg-gray-100 text-gray-500 border-gray-200'" class="px-3 py-1 text-xs font-bold rounded-full border shadow-sm transition-colors">
                {{ item.is_active ? '✅ 已啟用' : '⏸️ 已暫停' }}
              </button>
            </td>
            <td class="px-5 py-3 text-right">
              <button @click="deleteSchedule(item.id)" class="text-red-500 hover:text-red-700 hover:underline text-sm font-bold">刪除</button>
            </td>
          </tr>
          <tr v-if="schedules.length === 0">
            <td colspan="3" class="px-5 py-8 text-center text-gray-400">目前沒有設定任何排程</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
const supabase = useSupabaseClient()
const runtimeConfig = useRuntimeConfig()
const cronBridgeUrl = computed(() => String(runtimeConfig.public.cronBridgeUrl || '').replace(/\/$/, ''))

const schedules = ref([])
const newTime = ref('08:00')
const isTesting = ref(false)
const testMessage = ref('')
const testSucceeded = ref(false)

const copyCronUrl = async () => {
  await navigator.clipboard.writeText(cronBridgeUrl.value)
  alert('已複製新的 cron-job.org 網址')
}

const testCronBridge = async () => {
  isTesting.value = true
  testMessage.value = ''
  testSucceeded.value = false
  try {
    await $fetch(cronBridgeUrl.value, { cache: 'no-store' })
    testSucceeded.value = true
    testMessage.value = '✅ Vercel 轉接正常（HTTP 204 空內容），Render 喚醒要求已排入背景執行。'
  } catch (error) {
    testMessage.value = `❌ 喚醒測試失敗：${error?.data?.message || error?.message || '無法連線'}`
  } finally {
    isTesting.value = false
  }
}

const loadSchedules = async () => {
  const { data } = await supabase.from('wakeup_schedules').select('*').order('time_str', { ascending: true })
  if (data) schedules.value = data
}

const addSchedule = async () => {
  if (!newTime.value) return alert('請選擇時間！')
  await supabase.from('wakeup_schedules').insert([{ time_str: newTime.value }])
  newTime.value = '08:00'
  loadSchedules()
}

const toggleStatus = async (item) => {
  await supabase.from('wakeup_schedules').update({ is_active: !item.is_active }).eq('id', item.id)
  loadSchedules()
}

const deleteSchedule = async (id) => {
  if (confirm('確定要刪除這個時段嗎？')) {
    await supabase.from('wakeup_schedules').delete().eq('id', id)
    loadSchedules()
  }
}

onMounted(() => { loadSchedules() })
</script>
