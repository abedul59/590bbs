<template>
  <div class="space-y-8 animate-fade-in">
    
    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div class="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-2">
        <h3 class="text-xl font-semibold flex items-center gap-2 text-indigo-900">
          🎙️ Telegram 錄音證據批次上傳中心
          <span class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded shadow-sm border border-red-200">法律證據專用 (含指紋)</span>
        </h3>
        <button @click="wakeUpTgServer" :disabled="tgWakeUpCountdown > 0" class="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-4 py-2 rounded-lg shadow transition-colors flex items-center gap-2 disabled:opacity-70">
          <span v-if="tgWakeUpCountdown > 0">⏳ 伺服器喚醒中... ({{ tgWakeUpCountdown }}s)</span>
          <span v-else>🛸 獨立喚醒 TG 上傳伺服器</span>
        </button>
      </div>
      
      <div class="bg-indigo-50 border border-indigo-200 p-4 md:p-6 rounded-xl shadow-sm relative">
        <div class="flex flex-col md:flex-row md:items-start gap-4 mb-4">
          <div class="md:w-1/4">
            <label class="block text-sm font-bold text-indigo-900 mb-1">目標 Topic ID (月份)</label>
            <input v-model="tgEvidenceTopicId" type="number" placeholder="例: 45" class="border border-indigo-300 p-2 w-full rounded focus:ring-2 focus:ring-indigo-400 bg-white shadow-sm">
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
            <textarea v-model="tgEvidenceCaption" placeholder="例如：刑法總則第五章..." class="border border-indigo-300 p-2 w-full rounded bg-white shadow-sm rows-2"></textarea>
        </div>

        <div class="flex flex-col md:flex-row items-center gap-4 pt-2 border-t border-indigo-200">
          <button @click="submitEvidenceBatchUpload" :disabled="selectedEvidenceFiles.length === 0 || isEvidenceUploading" class="w-full md:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2.5 px-6 rounded-lg shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
            <span v-if="isEvidenceUploading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>{{ isEvidenceUploading ? `排隊上傳中 (${currentEvidenceUploadIndex}/${selectedEvidenceFiles.length})...` : '🚀 開始保全批次上傳' }}</span>
          </button>
          <div v-if="evidenceUploadStatus" class="flex-1 px-3 py-2 rounded-lg text-sm font-bold" :class="evidenceUploadStatus.includes('❌') ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'">{{ evidenceUploadStatus }}</div>
        </div>

        <div v-if="tgEvidenceResults.length > 0" class="mt-6 bg-white border-2 border-green-400 p-4 rounded-lg shadow-sm animate-fade-in">
          <div class="flex justify-between items-center border-b border-green-200 pb-2 mb-3">
            <h4 class="text-green-700 font-bold">✅ 成功保全 {{ tgEvidenceResults.length }} 筆證據</h4>
            <button @click="batchSaveToTgTodo" class="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors">📝 全部加入 TG 獨立暫存清單</button>
          </div>
          <ul class="space-y-4 max-h-[300px] overflow-y-auto pr-2">
            <li v-for="(res, idx) in tgEvidenceResults" :key="idx" class="bg-gray-50 p-3 rounded border border-gray-200 text-sm">
              <p><span class="font-bold text-gray-600">檔名：</span>{{ res.filename }}</p>
              <p class="my-1 flex items-center gap-2"><span class="font-bold text-gray-600">連結：</span> <a :href="res.telegram_link" target="_blank" class="text-blue-600 hover:underline truncate">{{ res.telegram_link }}</a></p>
              <p class="flex flex-col"><span class="font-bold text-gray-600">SHA-256 指紋：</span> <code class="bg-white p-1 rounded border border-gray-200 text-xs text-gray-800 break-all mt-1">{{ res.file_hash }}</code></p>
              <div class="mt-2 text-right"><button @click="copyToClipboard(`錄音檔：${res.filename}\n連結：${res.telegram_link}\n指紋：${res.file_hash}`)" class="text-xs text-gray-500 hover:text-gray-800 font-bold underline">📋 複製單筆</button></div>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div class="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-3">
        <h3 class="text-xl font-semibold flex items-center gap-2 text-indigo-900">
          📁 TG 獨立暫存清單 
          <span class="text-xs text-gray-400 font-normal border px-2 py-1 rounded">證據與草稿專屬</span>
        </h3>
        <div class="flex gap-2">
          <input type="file" accept=".csv" ref="tgTodoCsvInput" class="hidden" @change="handleTgTodoCsvImport">
          <button @click="() => tgTodoCsvInput.click()" class="text-xs bg-gray-100 border border-gray-300 text-gray-700 font-bold px-3 py-1.5 rounded shadow-sm hover:bg-gray-200 transition-colors">📥 匯入 CSV</button>
          <button @click="exportTgTodosCSV" class="text-xs bg-indigo-600 text-white font-bold px-3 py-1.5 rounded shadow-sm hover:bg-indigo-700 transition-colors">📤 匯出 CSV</button>
        </div>
      </div>
      <ul class="space-y-2 max-h-[300px] overflow-y-auto pr-2">
        <li v-for="item in tgTodosList" :key="item.id" :class="['flex justify-between items-center p-3 rounded-lg border transition-all duration-200', item.is_completed ? 'bg-gray-50 border-gray-200 opacity-60' : 'bg-indigo-50 border-indigo-200 shadow-sm']">
          <div class="flex items-center gap-3 overflow-hidden">
            <input type="checkbox" :checked="item.is_completed" @change="toggleTgTodo(item)" class="w-5 h-5 cursor-pointer text-indigo-600">
            <div class="flex flex-col">
              <span :class="['font-medium text-gray-800 whitespace-pre-wrap text-sm', {'line-through text-gray-500': item.is_completed}]">{{ item.content }}</span>
              <a v-if="item.url" :href="item.url" target="_blank" class="text-blue-500 text-xs hover:underline mt-1 w-fit">🔗 Telegram 連結</a>
            </div>
          </div>
          <button @click="deleteTgTodo(item.id)" class="text-gray-400 hover:text-red-500 p-1.5 rounded transition-colors">✖</button>
        </li>
        <li v-if="tgTodosList.length === 0" class="text-sm text-gray-400 py-4 text-center bg-gray-50 rounded-lg border border-dashed border-gray-300">目前 TG 獨立暫存清單中沒有資料。</li>
      </ul>
    </section>

    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div class="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-2 border-b border-gray-100 pb-4">
        <h3 class="text-xl font-semibold flex items-center gap-2 text-teal-800">
          📚 Telegram 上課教材中心
          <span class="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded shadow-sm border border-teal-200">大型影片與講義專區 (雙向)</span>
        </h3>
        <div class="flex gap-2">
          <input type="file" accept=".csv" ref="tgMaterialCsvInput" class="hidden" @change="handleMaterialCsvImport">
          <button @click="() => tgMaterialCsvInput.click()" class="text-xs bg-white border border-gray-300 text-gray-700 font-bold px-3 py-1.5 rounded shadow-sm hover:bg-gray-100 transition-colors">📥 匯入教材清單</button>
          <button @click="exportMaterialsCSV" class="text-xs bg-teal-600 text-white font-bold px-3 py-1.5 rounded shadow-sm hover:bg-teal-700 transition-colors">📤 匯出教材清單</button>
        </div>
      </div>

      <div class="bg-teal-50 border border-teal-200 p-4 md:p-6 rounded-xl shadow-sm mb-6">
        <h4 class="font-bold text-teal-900 mb-4 flex items-center gap-1">⬆️ 上傳新教材</h4>
        
        <div class="flex flex-col md:flex-row md:items-start gap-4 mb-4">
          <div class="md:w-1/4">
            <label class="block text-sm font-bold text-teal-900 mb-1">目標 Topic ID (分類)</label>
            <input v-model="tgMaterialTopicId" type="number" placeholder="例: 99" class="border border-teal-300 p-2 w-full rounded focus:ring-2 focus:ring-teal-400 bg-white shadow-sm outline-none">
          </div>
          <div class="flex-1">
            <label class="block text-sm font-bold text-teal-900 mb-1">選擇教材檔案 (支援影片 .mp4、文件、壓縮檔，可多選)</label>
            <input type="file" accept="video/mp4,video/x-m4v,video/*,application/pdf,application/zip,application/x-rar-compressed,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" multiple ref="tgMaterialFileInput" @change="selectMaterialFiles" :disabled="isMaterialUploading" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-bold file:bg-teal-200 file:text-teal-800 hover:file:bg-teal-300 cursor-pointer bg-white border border-teal-300 rounded shadow-sm disabled:opacity-50 transition-colors">
          </div>
        </div>

        <div v-if="selectedMaterialFiles.length > 0 && !isMaterialUploading" class="mb-4 bg-white border border-teal-100 rounded-lg p-3 max-h-[150px] overflow-y-auto text-sm">
          <p class="font-bold text-teal-800 mb-2">已選擇 {{ selectedMaterialFiles.length }} 個教材檔案：</p>
          <ul class="list-disc pl-5 text-gray-600"><li v-for="file in selectedMaterialFiles" :key="file.name">{{ file.name }} <span class="text-xs text-gray-400">({{(file.size / 1024 / 1024).toFixed(2)}} MB)</span></li></ul>
        </div>

        <div class="mb-4">
            <label class="block text-sm font-bold text-teal-900 mb-1">教材說明 (例：第五章上課錄影)</label>
            <textarea v-model="tgMaterialCaption" placeholder="請輸入說明..." class="border border-teal-300 p-2 w-full rounded bg-white shadow-sm rows-2 outline-none focus:ring-2 focus:ring-teal-400"></textarea>
        </div>

        <div class="flex flex-col md:flex-row items-center gap-4 pt-2 border-t border-teal-200">
          <button @click="submitMaterialBatchUpload" :disabled="selectedMaterialFiles.length === 0 || isMaterialUploading" class="w-full md:w-auto bg-teal-600 hover:bg-teal-700 text-white font-bold py-2.5 px-6 rounded-lg shadow-md transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
            <span v-if="isMaterialUploading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            <span>{{ isMaterialUploading ? `教材上傳中 (${currentMaterialUploadIndex}/${selectedMaterialFiles.length})...` : '⬆️ 批次上傳教材' }}</span>
          </button>
          <div v-if="materialUploadStatus" class="flex-1 px-3 py-2 rounded-lg text-sm font-bold" :class="materialUploadStatus.includes('❌') ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-teal-100 text-teal-800 border border-teal-300'">{{ materialUploadStatus }}</div>
        </div>
      </div>

      <div>
        <h4 class="font-bold text-teal-900 mb-3 flex items-center justify-between">
          <span>☁️ 雲端教材庫 (快速下載)</span>
          <span class="text-xs font-normal text-gray-500 border border-gray-200 px-2 py-1 rounded bg-gray-50">共 {{ tgMaterialsList.length }} 筆教材</span>
        </h4>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[500px] overflow-y-auto pr-2">
          <div v-for="mat in tgMaterialsList" :key="mat.id" class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow relative group flex flex-col">
            <button @click="deleteMaterial(mat.id)" class="absolute top-3 right-3 text-gray-300 hover:text-red-500 font-bold opacity-0 group-hover:opacity-100 transition-opacity">✖</button>
            
            <div class="flex items-center gap-2 mb-2">
              <span class="bg-teal-100 text-teal-800 text-[10px] font-bold px-2 py-0.5 rounded">Topic {{ mat.topic_id || '無' }}</span>
              <span class="text-[10px] text-gray-400 font-mono">🕒 {{ formatDate(mat.created_at) }}</span>
            </div>
            
            <h5 class="font-bold text-gray-800 break-all leading-tight mb-2 pr-6">{{ mat.filename }}</h5>
            
            <div class="flex items-center gap-2 mb-3 text-xs">
              <span v-if="mat.file_size" class="bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">{{ mat.file_size }} MB</span>
            </div>

            <p v-if="mat.caption" class="text-sm text-gray-600 whitespace-pre-wrap flex-1 mb-4 bg-gray-50 p-2 rounded border border-gray-100">{{ mat.caption }}</p>
            <div v-else class="flex-1 mb-4"></div> <div class="flex flex-wrap gap-2 mt-auto border-t border-gray-100 pt-3">
              <a :href="mat.url" target="_blank" class="bg-teal-500 hover:bg-teal-600 text-white px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors text-center flex-1">🔗 開啟 / 下載</a>
              <button @click="copyToClipboard(mat.url)" class="bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-300 px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors text-center flex-1">📋 複製連結</button>
            </div>
          </div>
          
          <div v-if="tgMaterialsList.length === 0" class="col-span-1 md:col-span-2 text-center py-10 text-gray-400 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50">
            目前雲端沒有任何教材。
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const supabase = useSupabaseClient()
const dayjs = useDayjs()

// ====== 共用工具 ======
const formatDate = (dateString) => dayjs(dateString).format('YYYY/MM/DD HH:mm')
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

onMounted(() => { 
  loadTgTodos()
  loadMaterials()
})

// ====== 獨立喚醒按鈕邏輯 ======
const tgWakeUpCountdown = ref(0)
const showRenderToast = ref(false)
const wakeUpTgServer = async () => {
  tgWakeUpCountdown.value = 60
  try { await fetch('https://tg-uploader-api.onrender.com/?_ping_ts='+Date.now(), { mode: 'no-cors' }) } catch(e){}
  const timer = setInterval(() => { 
    tgWakeUpCountdown.value--; 
    if (tgWakeUpCountdown.value <= 0) {
      clearInterval(timer); showRenderToast.value = true; setTimeout(() => { showRenderToast.value = false }, 10000)
    }
  }, 1000)
}

// ====== 區塊 1：錄音證據批次保全 ======
const tgEvidenceTopicId = ref(''); const tgEvidenceCaption = ref(''); const isEvidenceUploading = ref(false); const evidenceUploadStatus = ref(''); const selectedEvidenceFiles = ref([]); const currentEvidenceUploadIndex = ref(0); const tgEvidenceResults = ref([]); const tgEvidenceFileInput = ref(null)

const selectEvidenceFiles = (e) => { 
  selectedEvidenceFiles.value = Array.from(e.target.files); 
  evidenceUploadStatus.value = selectedEvidenceFiles.value.length ? `已選 ${selectedEvidenceFiles.value.length} 檔，準備保全` : ''; 
  tgEvidenceResults.value = [] 
}

const submitEvidenceBatchUpload = async () => {
  if (!tgEvidenceTopicId.value) return alert('請輸入 Topic ID')
  isEvidenceUploading.value = true; tgEvidenceResults.value = []; let hasError = false
  
  for (let i = 0; i < selectedEvidenceFiles.value.length; i++) {
    const file = selectedEvidenceFiles.value[i]; currentEvidenceUploadIndex.value = i + 1; evidenceUploadStatus.value = `保全上傳中 (${i+1}/${selectedEvidenceFiles.value.length})...`
    const fd = new FormData(); fd.append('file', file); fd.append('topic_id', tgEvidenceTopicId.value)
    
    let cap = `📂 證據檔：${file.name}\n🕒 時間：${dayjs().format('YYYY/MM/DD HH:mm')}`; 
    if(tgEvidenceCaption.value) cap += `\n📝 說明：${tgEvidenceCaption.value}`; 
    fd.append('caption', cap)
    // 提醒：若你的 FastAPI 未關閉 hash 運算，此處依舊會計算並回傳
    try {
      const res = await fetch('https://tg-uploader-api.onrender.com/upload/', { method: 'POST', body: fd })
      if (!res.headers.get("content-type")?.includes("application/json")) throw new Error(`伺服器未喚醒`)
      const data = await res.json()
      if (data.success) tgEvidenceResults.value.push(data)
    } catch (e) { hasError = true }
  }
  isEvidenceUploading.value = false; selectedEvidenceFiles.value = []; if(tgEvidenceFileInput.value) tgEvidenceFileInput.value.value = ''; tgEvidenceCaption.value = ''
  evidenceUploadStatus.value = hasError ? (tgEvidenceResults.value.length ? '⚠️ 部分失敗' : '❌ 上傳失敗') : '✅ 批次保全完成'
}

// ====== 區塊 2：TG 獨立暫存清單 (tg_todos) ======
const tgTodosList = ref([]); const tgTodoCsvInput = ref(null)
const loadTgTodos = async () => { const { data } = await supabase.from('tg_todos').select('*').order('created_at', { ascending: false }); if(data) tgTodosList.value = data }

const batchSaveToTgTodo = async () => {
  for (const r of tgEvidenceResults.value) await supabase.from('tg_todos').insert([{ content: `[證據] ${r.filename}\n指紋: ${r.file_hash}`, url: r.telegram_link, is_completed: false }])
  loadTgTodos(); alert('已加入暫存清單！')
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

// ====== 區塊 3：Telegram 上課教材中心 (tg_materials) ======
const tgMaterialsList = ref([])
const tgMaterialTopicId = ref(''); const tgMaterialCaption = ref(''); const isMaterialUploading = ref(false); const materialUploadStatus = ref(''); const selectedMaterialFiles = ref([]); const currentMaterialUploadIndex = ref(0); const tgMaterialFileInput = ref(null); const tgMaterialCsvInput = ref(null)

const loadMaterials = async () => {
  const { data } = await supabase.from('tg_materials').select('*').order('created_at', { ascending: false })
  if (data) tgMaterialsList.value = data
}

const selectMaterialFiles = (e) => { 
  selectedMaterialFiles.value = Array.from(e.target.files)
  materialUploadStatus.value = selectedMaterialFiles.value.length ? `準備上傳 ${selectedMaterialFiles.value.length} 個教材` : ''
}

const submitMaterialBatchUpload = async () => {
  if (!tgMaterialTopicId.value) return alert('請輸入教材歸屬的 Topic ID')
  isMaterialUploading.value = true; let hasError = false; let successCount = 0
  
  for (let i = 0; i < selectedMaterialFiles.value.length; i++) {
    const file = selectedMaterialFiles.value[i]; currentMaterialUploadIndex.value = i + 1; materialUploadStatus.value = `教材上傳中 (${i+1}/${selectedMaterialFiles.value.length})...`
    const fd = new FormData(); fd.append('file', file); fd.append('topic_id', tgMaterialTopicId.value)
    
    // 教材的說明文案 (較輕鬆)
    let cap = `📚 教材：${file.name}\n上傳：${dayjs().format('YYYY/MM/DD HH:mm')}`; 
    if(tgMaterialCaption.value) cap += `\n📝 說明：${tgMaterialCaption.value}`; 
    fd.append('caption', cap)
    
    try {
      const res = await fetch('https://tg-material-api.onrender.com/upload/', { method: 'POST', body: fd })
      if (!res.headers.get("content-type")?.includes("application/json")) throw new Error(`伺服器未喚醒`)
      const data = await res.json()
      
      if (data.success) {
        // 上傳成功，直接寫入 Supabase tg_materials 資料表
        const fileSizeMB = (file.size / 1024 / 1024).toFixed(2)
        await supabase.from('tg_materials').insert([{ 
          filename: file.name, 
          url: data.telegram_link, 
          topic_id: parseInt(tgMaterialTopicId.value), 
          caption: tgMaterialCaption.value || null,
          file_size: fileSizeMB
        }])
        successCount++
      }
    } catch (e) { hasError = true }
  }
  
  isMaterialUploading.value = false; selectedMaterialFiles.value = []; if(tgMaterialFileInput.value) tgMaterialFileInput.value.value = ''; tgMaterialCaption.value = ''
  materialUploadStatus.value = hasError ? (successCount ? '⚠️ 部分教材上傳失敗' : '❌ 上傳失敗') : `✅ 成功上傳 ${successCount} 份教材！`
  loadMaterials() // 重新載入列表
}

const deleteMaterial = async (id) => {
  if(confirm('確定要從雲端教材庫移除此筆紀錄嗎？ (此動作不會刪除 TG 群組內的實體檔案)')) {
    await supabase.from('tg_materials').delete().eq('id', id)
    loadMaterials()
  }
}

const exportMaterialsCSV = () => {
  if (!tgMaterialsList.value.length) return alert('無資料可以匯出！')
  let csv = '檔名(filename),網址(url),Topic ID(topic_id),檔案大小(file_size),說明(caption)\n'
  tgMaterialsList.value.forEach(m => {
    csv += `"${(m.filename||'').replace(/"/g, '""')}","${m.url||''}",${m.topic_id||''},"${m.file_size||''}","${(m.caption||'').replace(/"/g, '""')}"\n`
  })
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob(['\uFEFF' + csv])); a.download = `TG教材庫_${dayjs().format('YYYYMMDD')}.csv`; a.click()
}

const handleMaterialCsvImport = async (e) => {
  const reader = new FileReader(); reader.onload = async (ev) => {
    const rows = parseCSVString(ev.target.result); const ins = []
    for(let i=1; i<rows.length; i++) {
      if(rows[i].length>=5) {
        ins.push({ filename: rows[i][0], url: rows[i][1], topic_id: rows[i][2] ? parseInt(rows[i][2]) : null, file_size: rows[i][3], caption: rows[i][4] })
      }
    }
    if(ins.length) { await supabase.from('tg_materials').insert(ins); alert(`成功匯入 ${ins.length} 筆教材庫紀錄！`); loadMaterials() }
  }; reader.readAsText(e.target.files[0]); tgMaterialCsvInput.value.value = ''
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce-in { 0% { transform: translateY(150%); opacity: 0; } 50% { transform: translateY(-10%); } 100% { transform: translateY(0); opacity: 1; } }
.animate-bounce-in { animation: bounce-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
</style>