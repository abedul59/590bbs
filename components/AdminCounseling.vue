<template>
  <div class="space-y-6 animate-fade-in">
    <section class="rounded-xl border border-sky-100 bg-white p-4 shadow-sm md:p-6">
      <div class="flex flex-col gap-3 border-b border-sky-100 pb-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 class="text-xl font-bold text-sky-950">📝 SHJHS 輔導紀錄中心</h3>
          <p class="mt-1 text-sm text-gray-500">整合文字日誌、錄音證據與舊系統資料轉移。</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <input ref="backupInput" type="file" accept="application/json,.json" class="hidden" @change="importBackup">
          <button class="rounded-lg border border-gray-300 bg-gray-50 px-3 py-2 text-sm font-bold text-gray-700 hover:bg-gray-100" @click="backupInput?.click()">
            📥 匯入舊紀錄
          </button>
          <button class="rounded-lg bg-sky-700 px-3 py-2 text-sm font-bold text-white hover:bg-sky-800" @click="exportBackup">
            📤 匯出完整備份
          </button>
        </div>
      </div>

      <div v-if="databaseError" class="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
        {{ databaseError }}
      </div>
      <div v-if="notice" class="mt-4 rounded-lg border p-3 text-sm font-bold" :class="notice.startsWith('❌') ? 'border-red-200 bg-red-50 text-red-700' : 'border-green-200 bg-green-50 text-green-700'">
        {{ notice }}
      </div>
    </section>

    <section class="rounded-xl border border-gray-100 bg-white p-4 shadow-sm md:p-6">
      <h3 class="mb-4 text-lg font-bold text-gray-800">新增文字紀錄</h3>
      <div class="grid gap-3 md:grid-cols-[180px_1fr]">
        <label class="text-sm font-bold text-gray-700">
          紀錄日期
          <input v-model="newRecordDate" type="date" class="mt-1 w-full rounded-lg border border-gray-300 p-2.5 font-normal outline-none focus:ring-2 focus:ring-sky-400">
        </label>
        <label class="text-sm font-bold text-gray-700">
          紀錄內容
          <textarea v-model="newContent" rows="5" placeholder="輸入或使用手機語音輸入輔導紀錄…" class="mt-1 w-full rounded-lg border border-gray-300 p-3 font-normal leading-relaxed outline-none focus:ring-2 focus:ring-sky-400" />
        </label>
      </div>
      <div class="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <span class="text-xs text-gray-400">{{ savingRecord ? '自動儲存中…' : lastSavedTime ? `${lastSavedTime} 已儲存` : '停止輸入 1.5 秒後自動儲存' }}</span>
        <div class="flex justify-end gap-2">
          <button :disabled="savingRecord || !draftSaved" class="rounded-lg bg-gray-200 px-4 py-2.5 font-bold text-gray-700 disabled:opacity-50" @click="startNewRecord">
            新增下一筆
          </button>
          <button :disabled="savingRecord || !newContent.trim()" class="rounded-lg bg-sky-700 px-5 py-2.5 font-bold text-white disabled:opacity-50" @click="saveDraft(true)">
            {{ savingRecord ? '儲存中…' : '立即儲存' }}
          </button>
        </div>
      </div>
    </section>

    <section class="rounded-xl border border-gray-100 bg-white p-4 shadow-sm md:p-6">
      <div class="mb-4 flex items-center justify-between">
        <button class="rounded-lg bg-gray-100 p-2 hover:bg-gray-200" @click="changeMonth(-1)">⬅️</button>
        <h3 class="text-lg font-bold text-gray-800">{{ calendarYear }} 年 {{ calendarMonth + 1 }} 月</h3>
        <button class="rounded-lg bg-gray-100 p-2 hover:bg-gray-200" @click="changeMonth(1)">➡️</button>
      </div>
      <div class="mb-2 grid grid-cols-7 gap-1 text-center text-xs font-bold text-gray-400">
        <div v-for="day in weekDays" :key="day">{{ day }}</div>
      </div>
      <div class="grid grid-cols-7 gap-1 md:gap-2">
        <div v-for="(day, index) in calendarDays" :key="index" class="aspect-square">
          <button
            v-if="day"
            class="relative flex h-full w-full flex-col items-center justify-center rounded-lg border text-sm transition md:rounded-xl"
            :class="selectedDate === day.date ? 'border-sky-500 bg-sky-100 ring-2 ring-sky-400' : day.hasRecord ? 'border-sky-200 bg-sky-50 text-sky-800' : 'border-gray-100 bg-white text-gray-600 hover:bg-gray-50'"
            @click="selectDate(day.date)"
          >
            <span class="font-bold">{{ day.day }}</span>
            <span v-if="day.hasRecord" class="mt-1 h-1.5 w-1.5 rounded-full bg-sky-500" />
          </button>
        </div>
      </div>
    </section>

    <section v-if="selectedDate" class="space-y-4">
      <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <h3 class="text-xl font-bold text-gray-800">{{ selectedDate }} 的紀錄</h3>
        <span class="text-sm text-gray-500">文字 {{ dayLogs.length }} 筆・錄音 {{ evidenceList.length }} 筆</span>
      </div>

      <div v-if="loadingDay" class="rounded-xl border border-dashed bg-white p-8 text-center text-gray-500">載入中…</div>
      <template v-else>
        <article v-for="(log, index) in dayLogs" :key="log.id" class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          <div class="mb-3 flex items-center justify-between">
            <span class="rounded bg-gray-100 px-2 py-1 text-xs font-bold text-gray-500">文字紀錄 #{{ index + 1 }}</span>
            <span class="text-xs text-gray-400">{{ formatDateTime(log.updated_at) }}</span>
          </div>
          <template v-if="editingId === log.id">
            <textarea v-model="editContent" rows="6" class="w-full rounded-lg border-2 border-sky-300 bg-sky-50 p-3 leading-relaxed outline-none" />
            <div class="mt-3 flex justify-end gap-2">
              <button class="rounded-lg bg-gray-200 px-4 py-2 font-bold text-gray-700" @click="cancelEdit">取消</button>
              <button class="rounded-lg bg-sky-700 px-4 py-2 font-bold text-white" @click="saveEdit(log.id)">儲存修改</button>
            </div>
          </template>
          <template v-else>
            <p class="whitespace-pre-wrap leading-relaxed text-gray-800">{{ log.content }}</p>
            <div class="mt-4 flex justify-end gap-2 border-t pt-3">
              <button class="rounded-md bg-red-50 px-3 py-1.5 text-sm font-bold text-red-600" @click="deleteLog(log.id)">刪除</button>
              <button class="rounded-md bg-sky-50 px-3 py-1.5 text-sm font-bold text-sky-700" @click="startEdit(log)">編輯</button>
            </div>
          </template>
        </article>
        <p v-if="dayLogs.length === 0" class="rounded-xl border border-dashed bg-white p-5 text-center text-sm text-gray-400">本日尚無文字紀錄</p>
      </template>
    </section>

    <section v-if="selectedDate" class="rounded-xl border border-indigo-100 bg-white p-4 shadow-sm md:p-6">
      <h3 class="text-lg font-bold text-indigo-950">🎙️ 錄音證據</h3>
      <p class="mt-1 text-sm text-gray-500">檔案會上傳至 SHJHS 專用 Render API，並保存 Telegram 連結與 SHA-256 指紋。</p>

      <div class="mt-4 grid gap-3 md:grid-cols-[180px_1fr]">
        <label class="text-sm font-bold text-gray-700">
          Telegram Topic ID
          <input v-model="topicId" type="number" placeholder="例如：45" class="mt-1 w-full rounded-lg border border-indigo-200 p-2.5 font-normal outline-none focus:ring-2 focus:ring-indigo-400">
        </label>
        <label class="text-sm font-bold text-gray-700">
          選擇錄音檔（可多選）
          <input ref="evidenceInput" type="file" multiple accept="audio/*,video/3gpp,video/3gpp2,audio/3gpp,audio/3gpp2,.wav,.mp3,.m4a,.aac,.ogg,.flac,.amr,.wma,.3gp,.3gpp" :disabled="uploading" class="mt-1 block w-full rounded-lg border border-indigo-200 bg-white text-sm file:mr-3 file:border-0 file:bg-indigo-100 file:px-4 file:py-2.5 file:font-bold file:text-indigo-800" @change="selectEvidenceFiles">
        </label>
      </div>
      <button :disabled="uploading || selectedFiles.length === 0 || !topicId" class="mt-4 w-full rounded-lg bg-indigo-600 px-5 py-3 font-bold text-white disabled:opacity-50 md:w-auto" @click="uploadEvidence">
        {{ uploading ? `上傳中（${uploadIndex}/${selectedFiles.length}）…` : `上傳 ${selectedFiles.length || ''} 筆錄音證據` }}
      </button>

      <ul class="mt-5 space-y-3">
        <li v-for="item in evidenceList" :key="item.id" class="rounded-lg border border-gray-200 bg-gray-50 p-3">
          <div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
            <div class="min-w-0">
              <p class="break-all font-bold text-gray-800">{{ item.title || item.file_name }}</p>
              <code v-if="item.file_hash" class="mt-1 block break-all text-xs text-gray-500">SHA-256: {{ item.file_hash }}</code>
            </div>
            <div class="flex shrink-0 flex-wrap gap-2">
              <a v-if="item.message_id" :href="downloadUrl(item.message_id)" target="_blank" rel="noopener noreferrer" class="rounded bg-indigo-600 px-3 py-1.5 text-xs font-bold text-white">下載</a>
              <a v-if="item.telegram_url" :href="item.telegram_url" target="_blank" rel="noopener noreferrer" class="rounded border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-bold text-blue-700">TG 原文</a>
              <button class="rounded bg-red-50 px-3 py-1.5 text-xs font-bold text-red-600" @click="deleteEvidence(item.id)">刪除索引</button>
            </div>
          </div>
        </li>
      </ul>
      <p v-if="!loadingDay && evidenceList.length === 0" class="mt-4 rounded-lg border border-dashed p-4 text-center text-sm text-gray-400">本日尚無錄音證據</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const supabase = useSupabaseClient()
const config = useRuntimeConfig()
const apiUrl = computed(() => String(config.public.shjhsTelegramApiUrl || 'https://five90bbs-telegram-shjhs-api.onrender.com').replace(/\/$/, ''))

const toLocalDate = (date = new Date()) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const now = new Date()
const calendarYear = ref(now.getFullYear())
const calendarMonth = ref(now.getMonth())
const selectedDate = ref(toLocalDate(now))
const recordedDates = ref(new Set())
const dayLogs = ref([])
const evidenceList = ref([])
const loadingDay = ref(false)
const databaseError = ref('')
const notice = ref('')
const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const newRecordDate = ref(toLocalDate(now))
const newContent = ref('')
const savingRecord = ref(false)
const draftId = ref('')
const draftSaved = ref(false)
const lastSavedTime = ref('')
let autoSaveTimer
const editingId = ref(null)
const editContent = ref('')

const topicId = ref('')
const evidenceInput = ref(null)
const selectedFiles = ref([])
const uploading = ref(false)
const uploadIndex = ref(0)

const backupInput = ref(null)

const calendarDays = computed(() => {
  const result = []
  const firstDay = new Date(calendarYear.value, calendarMonth.value, 1).getDay()
  const totalDays = new Date(calendarYear.value, calendarMonth.value + 1, 0).getDate()
  for (let index = 0; index < firstDay; index += 1) result.push(null)
  for (let day = 1; day <= totalDays; day += 1) {
    const date = `${calendarYear.value}-${String(calendarMonth.value + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    result.push({ day, date, hasRecord: recordedDates.value.has(date) })
  }
  return result
})

const describeDatabaseError = (error) => {
  if (error?.code === 'PGRST205' || error?.message?.includes('schema cache')) {
    return '尚未建立 SHJHS 輔導紀錄資料表。請先執行專案 supabase/migrations 內的 SQL。'
  }
  return error?.message || '讀取資料庫失敗。'
}

const fetchMonthlyRecords = async () => {
  databaseError.value = ''
  const first = `${calendarYear.value}-${String(calendarMonth.value + 1).padStart(2, '0')}-01`
  const last = toLocalDate(new Date(calendarYear.value, calendarMonth.value + 1, 0))
  const [logsResult, evidenceResult] = await Promise.all([
    supabase.from('counseling_logs').select('record_date').gte('record_date', first).lte('record_date', last),
    supabase.from('evidence_logs').select('log_date').gte('log_date', first).lte('log_date', last)
  ])
  const error = logsResult.error || evidenceResult.error
  if (error) {
    databaseError.value = describeDatabaseError(error)
    recordedDates.value = new Set()
    return
  }
  recordedDates.value = new Set([
    ...(logsResult.data || []).map((row) => row.record_date),
    ...(evidenceResult.data || []).map((row) => row.log_date)
  ])
}

const loadDay = async () => {
  if (!selectedDate.value) return
  loadingDay.value = true
  databaseError.value = ''
  const [logsResult, evidenceResult] = await Promise.all([
    supabase.from('counseling_logs').select('*').eq('record_date', selectedDate.value).order('updated_at', { ascending: true }),
    supabase.from('evidence_logs').select('*').eq('log_date', selectedDate.value).order('created_at', { ascending: true })
  ])
  loadingDay.value = false
  const error = logsResult.error || evidenceResult.error
  if (error) {
    databaseError.value = describeDatabaseError(error)
    dayLogs.value = []
    evidenceList.value = []
    return
  }
  dayLogs.value = logsResult.data || []
  evidenceList.value = evidenceResult.data || []
}

const refresh = async () => Promise.all([fetchMonthlyRecords(), loadDay()])

const changeMonth = (offset) => {
  const date = new Date(calendarYear.value, calendarMonth.value + offset, 1)
  calendarYear.value = date.getFullYear()
  calendarMonth.value = date.getMonth()
}

const selectDate = (date) => {
  selectedDate.value = date
  newRecordDate.value = date
  editingId.value = null
}

const saveDraft = async (showNotice = false) => {
  if (!newContent.value.trim()) return
  if (!draftId.value) draftId.value = crypto.randomUUID()
  savingRecord.value = true
  if (showNotice) notice.value = ''
  const { error } = await supabase.from('counseling_logs').upsert({
    id: draftId.value,
    record_date: newRecordDate.value,
    content: newContent.value.trim(),
    updated_at: new Date().toISOString()
  }, { onConflict: 'id' })
  savingRecord.value = false
  if (error) {
    notice.value = `❌ 儲存失敗：${describeDatabaseError(error)}`
    return
  }
  draftSaved.value = true
  lastSavedTime.value = new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
  selectedDate.value = newRecordDate.value
  const selected = new Date(`${newRecordDate.value}T12:00:00`)
  calendarYear.value = selected.getFullYear()
  calendarMonth.value = selected.getMonth()
  if (showNotice) notice.value = '✅ 文字紀錄已儲存。'
  await refresh()
}

const startNewRecord = () => {
  newContent.value = ''
  draftId.value = crypto.randomUUID()
  draftSaved.value = false
  lastSavedTime.value = ''
}

const startEdit = (log) => {
  editingId.value = log.id
  editContent.value = log.content || ''
}

const cancelEdit = () => {
  editingId.value = null
  editContent.value = ''
}

const saveEdit = async (id) => {
  const { error } = await supabase.from('counseling_logs').update({ content: editContent.value.trim(), updated_at: new Date().toISOString() }).eq('id', id)
  if (error) {
    notice.value = `❌ 修改失敗：${error.message}`
    return
  }
  cancelEdit()
  notice.value = '✅ 文字紀錄已更新。'
  await loadDay()
}

const deleteLog = async (id) => {
  if (!confirm('確定要刪除這筆文字紀錄嗎？')) return
  const { error } = await supabase.from('counseling_logs').delete().eq('id', id)
  if (error) notice.value = `❌ 刪除失敗：${error.message}`
  else {
    notice.value = '✅ 文字紀錄已刪除。'
    await refresh()
  }
}

const selectEvidenceFiles = (event) => {
  selectedFiles.value = Array.from(event.target?.files || [])
}

const formatRecordingName = (file) => {
  const date = new Date(file.lastModified || Date.now())
  const pad = (value) => String(value).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}_${pad(date.getHours())}${pad(date.getMinutes())}_${file.name}`
}

const uploadEvidence = async () => {
  if (!topicId.value || selectedFiles.value.length === 0) return
  uploading.value = true
  notice.value = ''
  let saved = 0
  try {
    for (let index = 0; index < selectedFiles.value.length; index += 1) {
      uploadIndex.value = index + 1
      const file = selectedFiles.value[index]
      const fileName = formatRecordingName(file)
      const form = new FormData()
      form.append('file', file, fileName)
      form.append('topic_id', String(topicId.value))
      const response = await fetch(`${apiUrl.value}/upload/`, { method: 'POST', body: form })
      const result = await response.json().catch(() => ({}))
      if (!response.ok || !result.success) throw new Error(result.detail || `Render API 回應 ${response.status}`)
      const { error } = await supabase.from('evidence_logs').insert({
        log_date: selectedDate.value,
        title: fileName.replace(/\.[^.]+$/, ''),
        file_name: fileName,
        telegram_url: result.telegram_link,
        message_id: result.message_id,
        file_hash: result.file_hash || null
      })
      if (error) throw error
      saved += 1
    }
    notice.value = `✅ 已上傳並歸檔 ${saved} 筆錄音證據。`
    await refresh()
  } catch (error) {
    notice.value = `❌ 已完成 ${saved} 筆，後續上傳停止：${error.message}`
  } finally {
    uploading.value = false
    uploadIndex.value = 0
    selectedFiles.value = []
    if (evidenceInput.value) evidenceInput.value.value = ''
  }
}

const deleteEvidence = async (id) => {
  if (!confirm('確定要刪除這筆錄音證據索引嗎？Telegram 原始檔不會被刪除。')) return
  const { error } = await supabase.from('evidence_logs').delete().eq('id', id)
  if (error) notice.value = `❌ 刪除失敗：${error.message}`
  else {
    notice.value = '✅ 錄音證據索引已刪除。'
    await refresh()
  }
}

const downloadUrl = (messageId) => `${apiUrl.value}/download/${messageId}`

const readAll = async (table, orderColumn) => {
  const rows = []
  const pageSize = 1000
  for (let from = 0; ; from += pageSize) {
    const { data, error } = await supabase.from(table).select('*').order(orderColumn, { ascending: true }).range(from, from + pageSize - 1)
    if (error) throw error
    rows.push(...(data || []))
    if (!data || data.length < pageSize) return rows
  }
}

const exportBackup = async () => {
  notice.value = ''
  try {
    const [counselingLogs, evidenceLogs] = await Promise.all([
      readAll('counseling_logs', 'updated_at'),
      readAll('evidence_logs', 'created_at')
    ])
    const backup = {
      format: '590bbs-shjhs-records',
      version: 1,
      exported_at: new Date().toISOString(),
      counseling_logs: counselingLogs,
      evidence_logs: evidenceLogs
    }
    const link = document.createElement('a')
    link.href = URL.createObjectURL(new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' }))
    link.download = `SHJHS輔導紀錄_${toLocalDate()}.json`
    link.click()
    URL.revokeObjectURL(link.href)
    notice.value = `✅ 已匯出 ${counselingLogs.length} 筆文字與 ${evidenceLogs.length} 筆錄音索引。`
  } catch (error) {
    notice.value = `❌ 匯出失敗：${describeDatabaseError(error)}`
  }
}

const normalizeBackup = (value) => {
  if (!value || typeof value !== 'object') throw new Error('備份檔格式無效')
  const counselingLogs = Array.isArray(value.counseling_logs) ? value.counseling_logs : []
  const evidenceLogs = Array.isArray(value.evidence_logs)
    ? value.evidence_logs.map((row) => ({
        ...row,
        id: /^\d+$/.test(String(row.id)) ? `legacy:${row.id}` : String(row.id)
      }))
    : []
  if (counselingLogs.length === 0 && evidenceLogs.length === 0) throw new Error('備份檔沒有可匯入的紀錄')
  return { counselingLogs, evidenceLogs }
}

const importInBatches = async (table, rows) => {
  for (let index = 0; index < rows.length; index += 200) {
    const { error } = await supabase.from(table).upsert(rows.slice(index, index + 200), { onConflict: 'id' })
    if (error) throw error
  }
}

const importBackup = async (event) => {
  notice.value = ''
  try {
    const file = event.target?.files?.[0]
    if (!file) return
    const { counselingLogs, evidenceLogs } = normalizeBackup(JSON.parse(await file.text()))
    if (!confirm(`將匯入 ${counselingLogs.length} 筆文字與 ${evidenceLogs.length} 筆錄音索引；相同 ID 會更新，是否繼續？`)) return
    await importInBatches('counseling_logs', counselingLogs)
    await importInBatches('evidence_logs', evidenceLogs)
    notice.value = `✅ 轉移完成：文字 ${counselingLogs.length} 筆、錄音索引 ${evidenceLogs.length} 筆。`
    await refresh()
  } catch (error) {
    notice.value = `❌ 匯入失敗：${describeDatabaseError(error)}`
  } finally {
    if (backupInput.value) backupInput.value.value = ''
  }
}

const formatDateTime = (value) => value ? new Date(value).toLocaleString('zh-TW', { dateStyle: 'short', timeStyle: 'short' }) : ''

watch([calendarYear, calendarMonth], fetchMonthlyRecords)
watch(selectedDate, loadDay)
watch([newContent, newRecordDate], () => {
  draftSaved.value = false
  clearTimeout(autoSaveTimer)
  if (!newContent.value.trim()) return
  autoSaveTimer = setTimeout(() => saveDraft(false), 1500)
})
onMounted(() => {
  draftId.value = crypto.randomUUID()
  refresh()
})
onBeforeUnmount(() => clearTimeout(autoSaveTimer))
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
</style>
