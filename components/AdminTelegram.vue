<template>
  <div class="space-y-6 animate-fade-in relative">

    <div class="flex gap-2 border-b-2 border-indigo-200 pb-0">
      <button @click="switchSchool('SHJHS')" :class="activeSchool === 'SHJHS' ? 'bg-indigo-600 text-white shadow-md' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'" class="px-6 py-3 rounded-t-xl font-bold transition-colors">
        🏫 SHJHS (新化)
      </button>
      <button @click="switchSchool('GRJHS')" :class="activeSchool === 'GRJHS' ? 'bg-indigo-600 text-white shadow-md' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'" class="px-6 py-3 rounded-t-xl font-bold transition-colors">
        🏫 GRJHS (歸仁)
      </button>
    </div>

    <section class="bg-white p-6 rounded-b-xl rounded-tr-xl shadow-sm border border-gray-100">
      <div class="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-2 border-b border-gray-100 pb-4">
        <h3 class="text-xl font-semibold flex items-center gap-2 text-indigo-900">
          🎙️ Telegram 錄音證據批次上傳中心 - {{ activeSchool }}
          <span class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded shadow-sm border border-red-200">法律證據專用 (含指紋與雙向下載)</span>
        </h3>
      </div>
      
      <div class="bg-indigo-50 border border-indigo-200 p-4 md:p-6 rounded-xl shadow-sm relative">
        <div class="flex flex-col md:flex-row md:items-start gap-4 mb-4">
          <div class="md:w-1/4">
            <label class="block text-sm font-bold text-indigo-900 mb-1">目標 Topic ID (月份)</label>
            <input v-model="tgEvidenceTopicId" type="number" placeholder="例: 45" class="border border-indigo-300 p-2 w-full rounded focus:ring-2 focus:ring-indigo-400 bg-white shadow-sm outline-none">
          </div>
          <div class="flex-1">
            <label class="block text-sm font-bold text-indigo-900 mb-1">選擇聲音檔 (保全用，可多選)</label>
            <input type="file" accept="audio/*,video/3gpp,video/3gpp2,audio/3gpp,audio/3gpp2,.wav,.mp3,.m4a,.aac,.ogg,.flac,.amr,.wma,.3gp,.3gpp" multiple ref="tgEvidenceFileInput" @change="selectEvidenceFiles" :disabled="isEvidenceUploading" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-bold file:bg-indigo-200 file:text-indigo-800 hover:file:bg-indigo-300 cursor-pointer bg-white border border-indigo-300 rounded shadow-sm disabled:opacity-50 transition-colors">
          </div>
        </div>

        <div v-if="selectedEvidenceFiles.length > 0 && !isEvidenceUploading" class="mb-4 bg-white border border-indigo-100 rounded-lg p-3 max-h-[150px] overflow-y-auto text-sm">
          <p class="font-bold text-indigo-800 mb-2">已選擇 {{ selectedEvidenceFiles.length }} 個檔案：</p>
          <ul class="list-disc pl-5 text-gray-600"><li v-for="file in selectedEvidenceFiles" :key="file.name">{{ file.name }} <span class="text-xs text-gray-400">({{(file.size / 1024 / 1024).toFixed(2)}} MB)</span></li></ul>
        </div>

        <div class="mb-4">
            <label class="block text-sm font-bold text-indigo-900 mb-1">補充說明 (套用於整批檔案)</label>
            <textarea v-model="tgEvidenceCaption" placeholder="例如：刑法總則第五章..." class="border border-indigo-300 p-2 w-full rounded bg-white shadow-sm rows-2 outline-none focus:ring-2 focus:ring-indigo-400"></textarea>
        </div>

        <div class="flex flex-col md:flex-row items-center gap-4 pt-2 border-t border-indigo-200">
          <button @click="submitEvidenceBatchUpload" :disabled="selectedEvidenceFiles.length === 0 || isEvidenceUploading" class="w-full md:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2.5 px-6 rounded-lg shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
            <span v-if="isEvidenceUploading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>{{ isEvidenceUploading ? `排隊上傳中 (${currentEvidenceUploadIndex}/${selectedEvidenceFiles.length})...` : `🚀 保全批次上傳至 ${activeSchool}` }}</span>
          </button>
          <div v-if="evidenceUploadStatus" class="flex-1 px-3 py-2 rounded-lg text-sm font-bold" :class="evidenceUploadStatus.includes('❌') ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'">{{ evidenceUploadStatus }}</div>
        </div>

        <div v-if="tgEvidenceResults.length > 0" class="mt-6 bg-white border-2 border-green-400 p-4 rounded-lg shadow-sm animate-fade-in">
          <div class="flex justify-between items-center border-b border-green-200 pb-2 mb-3">
            <h4 class="text-green-700 font-bold">✅ 成功保全 {{ tgEvidenceResults.length }} 筆證據 ({{ activeSchool }})</h4>
            <button @click="batchSaveToTgTodo" class="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors">📝 全部加入 TG 獨立暫存清單</button>
          </div>
          <ul class="space-y-4 max-h-[300px] overflow-y-auto pr-2">
            <li v-for="(res, idx) in tgEvidenceResults" :key="idx" class="bg-gray-50 p-3 rounded border border-gray-200 text-sm">
              <p><span class="font-bold text-gray-600">檔名：</span>{{ res.filename }}</p>
              <p class="flex flex-col"><span class="font-bold text-gray-600">SHA-256 指紋：</span> <code class="bg-white p-1 rounded border border-gray-200 text-xs text-gray-800 break-all mt-1">{{ res.file_hash }}</code></p>
              
              <div class="mt-3 flex items-center justify-between border-t border-gray-200 pt-2">
                <div class="flex gap-2">
                  <a :href="`${currentApiUrl}/download/${res.message_id}`" target="_blank" class="bg-indigo-500 hover:bg-indigo-600 text-white px-2 py-1 rounded text-xs font-bold shadow-sm transition-colors text-center">📥 立即串流下載</a>
                  <a :href="res.telegram_link" target="_blank" class="text-blue-600 hover:bg-blue-50 border border-blue-200 px-2 py-1 rounded text-xs font-bold transition-colors">🔗 TG 原文</a>
                </div>
                <button @click="copyToClipboard(`[${activeSchool}] 錄音檔：${res.filename}\n連結：${res.telegram_link}\n指紋：${res.file_hash}`)" class="text-xs text-gray-500 hover:text-gray-800 font-bold underline">📋 複製單筆資訊</button>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mt-8">
      <div class="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-3">
        <h3 class="text-xl font-semibold flex items-center gap-2 text-indigo-900">
          📁 TG 獨立暫存清單 
          <span class="text-xs text-gray-400 font-normal border px-2 py-1 rounded">證據與草稿專屬 (雙校共用)</span>
        </h3>
        <div class="flex gap-2">
          <input type="file" accept=".csv" ref="tgTodoCsvInput" class="hidden" @change="handleTgTodoCsvImport">
          <button @click="() => tgTodoCsvInput.click()" class="text-xs bg-gray-100 border border-gray-300 text-gray-700 font-bold px-3 py-1.5 rounded shadow-sm hover:bg-gray-200 transition-colors">📥 匯入 CSV</button>
          <button @click="exportTgTodosCSV" class="text-xs bg-indigo-600 text-white font-bold px-3 py-1.5 rounded shadow-sm hover:bg-indigo-700 transition-colors">📤 匯出 CSV</button>
        </div>
      </div>
      <ul class="space-y-2 max-h-[300px] overflow-y-auto pr-2">
        <li v-for="item in tgTodosList" :key="item.id" :class="['flex justify-between items-start p-3 rounded-lg border transition-all duration-200', item.is_completed ? 'bg-gray-50 border-gray-200 opacity-60' : 'bg-indigo-50 border-indigo-200 shadow-sm']">
          <div class="flex items-start gap-3 overflow-hidden flex-1">
            <input type="checkbox" :checked="item.is_completed" @change="toggleTgTodo(item)" class="w-5 h-5 mt-0.5 cursor-pointer text-indigo-600">
            <div class="flex flex-col gap-1 w-full">
              <span :class="['font-medium text-gray-800 whitespace-pre-wrap text-sm', {'line-through text-gray-500': item.is_completed}]">{{ item.content }}</span>
              
              <div v-if="item.url" class="flex flex-wrap gap-2 mt-1">
                <a :href="getDownloadUrl(item.url, item.content)" target="_blank" class="bg-indigo-500 hover:bg-indigo-600 text-white px-2 py-1 rounded text-xs font-bold shadow-sm transition-colors text-center">📥 立即串流下載</a>
                <a :href="item.url" target="_blank" class="text-blue-600 hover:bg-blue-50 border border-blue-200 px-2 py-1 rounded text-xs font-bold transition-colors">🔗 TG 原文連結</a>
              </div>
            </div>
          </div>
          <button @click="deleteTgTodo(item.id)" class="text-gray-400 hover:text-red-500 p-1.5 rounded transition-colors ml-2">✖</button>
        </li>
        <li v-if="tgTodosList.length === 0" class="text-sm text-gray-400 py-4 text-center bg-gray-50 rounded-lg border border-dashed border-gray-300">目前 TG 獨立暫存清單中沒有資料。</li>
      </ul>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
const supabase = useSupabaseClient()
const dayjs = useDayjs()

// ====== 🌟 分頁與 API 網址設定 ======
const activeSchool = ref('SHJHS')

// ⚠️ 請在這裡替換您為 GRJHS 新建立的 Hugging Face API 網址！
const apiUrls = {
  'SHJHS': 'https://lawxstudents168-tg-uploader-api.hf.space',
  'GRJHS': 'https://lawxstudents168-tg-uploader-api-grjhs.hf.space' // <-- 請將這裡改為您的 GRJHS Space 網址
}

const currentApiUrl = computed(() => apiUrls[activeSchool.value])

// 切換學校時，自動清空底下的上傳表單，避免傳錯地方
const switchSchool = (school) => {
  activeSchool.value = school
  selectedEvidenceFiles.value = []
  tgEvidenceResults.value = []
  evidenceUploadStatus.value = ''
  tgEvidenceCaption.value = ''
  if(tgEvidenceFileInput.value) tgEvidenceFileInput.value.value = ''
}

// ====== 共用工具 ======
const copyToClipboard = async (text) => {
  try { await navigator.clipboard.writeText(text); alert('✅ 已複製！') } 
  catch (err) { alert('❌ 複製失敗') }
}
const parseCSVString = (str) => {
  const arr = []; let quote = false; let row = 0, col = 0
  for (let c = 0; c < str.length; c++) {
    let cc = str[c], nc = str[c+1]
    arr[row] = arr[row] || []; arr[row][col] = arr[row][col] || ''
    if (cc == '"' && quote && nc == '"') { arr[row][col] += cc; ++c; continue; }  
    if (cc == '"') { quote = !quote; continue; }
    if (cc == ',' && !quote) { ++col; continue; }
    if (cc == '\n' && !quote) { ++row; col = 0; continue; }
    if (cc == '\r' && !quote) continue
    arr[row][col] += cc
  }
  return arr.filter(r => r.length > 1 || r[0] !== '') 
}

onMounted(() => { loadTgTodos() })

// ====== 下載連結轉換邏輯 ======
const getDownloadUrl = (url, content) => {
  if (!url) return '#'
  if (!url.includes('t.me/c/')) return url
  const parts = url.split('/')
  const messageId = parts[parts.length - 1]
  
  // 透過內容裡面的標籤判斷要向哪一個伺服器要檔案
  let targetApi = apiUrls['SHJHS'] // 預設
  if (content && content.includes('[證據-GRJHS]')) {
    targetApi = apiUrls['GRJHS']
  }
  
  return `${targetApi}/download/${messageId}`
}

// ====== 區塊 1：錄音證據批次保全 ======
const tgEvidenceTopicId = ref(''); const tgEvidenceCaption = ref(''); const isEvidenceUploading = ref(false); const evidenceUploadStatus = ref(''); const selectedEvidenceFiles = ref([]); const currentEvidenceUploadIndex = ref(0); const tgEvidenceResults = ref([]); const tgEvidenceFileInput = ref(null)

const selectEvidenceFiles = (e) => { 
  selectedEvidenceFiles.value = Array.from(e.target.files); 
  evidenceUploadStatus.value = selectedEvidenceFiles.value.length ? `已選 ${selectedEvidenceFiles.value.length} 檔，準備保全至 ${activeSchool.value}` : ''; 
  tgEvidenceResults.value = [] 
}

const submitEvidenceBatchUpload = async () => {
  if (!tgEvidenceTopicId.value) return alert('請輸入 Topic ID')
  isEvidenceUploading.value = true; tgEvidenceResults.value = []; let hasError = false
  
  for (let i = 0; i < selectedEvidenceFiles.value.length; i++) {
    const file = selectedEvidenceFiles.value[i]; currentEvidenceUploadIndex.value = i + 1; evidenceUploadStatus.value = `保全上傳中 (${i+1}/${selectedEvidenceFiles.value.length})...`
    const fd = new FormData(); fd.append('file', file); fd.append('topic_id', tgEvidenceTopicId.value)
    
    let cap = `📂 證據檔：${file.name}\n🏫 歸屬：${activeSchool.value}\n🕒 時間：${dayjs().format('YYYY/MM/DD HH:mm')}`; 
    if(tgEvidenceCaption.value) cap += `\n📝 說明：${tgEvidenceCaption.value}`; 
    fd.append('caption', cap)
    
    try {
      // 🌟 自動根據選取的學校，發送到對應的 HF 伺服器
      const res = await fetch(`${currentApiUrl.value}/upload/`, { method: 'POST', body: fd })
      if (!res.headers.get("content-type")?.includes("application/json")) throw new Error(`伺服器無回應或超時`)
      const data = await res.json()
      if (data.success) tgEvidenceResults.value.push(data)
    } catch (e) { hasError = true }
  }
  isEvidenceUploading.value = false; selectedEvidenceFiles.value = []; if(tgEvidenceFileInput.value) tgEvidenceFileInput.value.value = ''; tgEvidenceCaption.value = ''
  evidenceUploadStatus.value = hasError ? (tgEvidenceResults.value.length ? '⚠️ 部分失敗' : '❌ 上傳失敗') : `✅ 批次保全完成 (${activeSchool.value})`
}

// ====== 區塊 2：TG 獨立暫存清單 (tg_todos) ======
const tgTodosList = ref([]); const tgTodoCsvInput = ref(null)
const loadTgTodos = async () => { const { data } = await supabase.from('tg_todos').select('*').order('created_at', { ascending: false }); if(data) tgTodosList.value = data }

const batchSaveToTgTodo = async () => {
  // 🌟 在存入資料庫時，自動加上學校標籤 [證據-SHJHS] 或 [證據-GRJHS]
  for (const r of tgEvidenceResults.value) await supabase.from('tg_todos').insert([{ content: `[證據-${activeSchool.value}] ${r.filename}\n指紋: ${r.file_hash}`, url: r.telegram_link, is_completed: false }])
  loadTgTodos(); alert(`已將 ${activeSchool.value} 證據加入暫存清單！`)
}
const toggleTgTodo = async (t) => { await supabase.from('tg_todos').update({ is_completed: !t.is_completed }).eq('id', t.id); loadTgTodos() }
const deleteTgTodo = async (id) => { if(confirm('刪除？')) { await supabase.from('tg_todos').delete().eq('id', id); loadTgTodos() } }

const exportTgTodosCSV = () => {
  if (!tgTodosList.value.length) return alert('無資料')
  let csv = '內容,網址,是否完成\n'
  tgTodosList.value.forEach(t => csv += `"${(t.content||'').replace(/"/g, '""')}","${t.url||''}",${t.is_completed?'TRUE':'FALSE'}\n`)
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['\uFEFF' + csv])); a.download = `TG清單_${dayjs().format('YYYYMMDD')}.csv`; a.click()
}
const handleTgTodoCsvImport = async (e) => {
  const reader = new FileReader(); reader.onload = async (ev) => {
    const rows = parseCSVString(ev.target.result); const ins = []
    for(let i=1; i<rows.length; i++) if(rows[i].length>=3) ins.push({ content: rows[i][0], url: rows[i][1], is_completed: rows[i][2].toUpperCase()==='TRUE' })
    if(ins.length) { await supabase.from('tg_todos').insert(ins); alert(`成功匯入 ${ins.length} 筆！`); loadTgTodos() }
  }; reader.readAsText(e.target.files[0]); tgTodoCsvInput.value.value = ''
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
