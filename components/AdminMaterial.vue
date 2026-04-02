<template>
  <div class="space-y-8 animate-fade-in relative">
    
    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div class="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-2 border-b border-gray-100 pb-4">
        <h3 class="text-xl font-semibold flex items-center gap-2 text-teal-800">
          📚 Telegram 上課教材中心
          <span class="text-xs bg-teal-100 text-teal-800 px-2 py-1 rounded shadow-sm border border-teal-200">大型影片與講義專區 (雙向)</span>
        </h3>
      </div>

      <div class="bg-teal-50 border border-teal-200 p-4 md:p-6 rounded-xl shadow-sm mb-8">
        <h4 class="font-bold text-teal-900 mb-4 flex items-center gap-1">⬆️ 上傳新教材</h4>
        
        <div class="flex flex-col md:flex-row md:items-start gap-4 mb-4">
          <div class="md:w-1/4">
            <label class="block text-sm font-bold text-teal-900 mb-1">目標 Topic ID (分類)</label>
            <input v-model="tgMaterialTopicId" type="number" placeholder="例: 99" class="border border-teal-300 p-2 w-full rounded focus:ring-2 focus:ring-teal-400 bg-white shadow-sm outline-none">
          </div>
          <div class="flex-1">
            <label class="block text-sm font-bold text-teal-900 mb-1">選擇教材檔案 (支援多選)</label>
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

      <div class="bg-indigo-50 border border-indigo-200 p-4 md:p-6 rounded-xl shadow-sm mb-8">
        <h4 class="font-bold text-indigo-900 mb-4 flex items-center gap-1">🔍 雲端教材即時搜尋 (免登入直接下)</h4>
        
        <div class="flex flex-col md:flex-row gap-2 mb-4">
          <input v-model="searchQuery" @keyup.enter="searchCloudFiles" type="text" placeholder="輸入教材名稱關鍵字 (例如: 第五章)..." class="border border-indigo-300 p-2 flex-1 rounded focus:ring-2 focus:ring-indigo-400 bg-white shadow-sm outline-none">
          <button @click="searchCloudFiles" :disabled="isSearching" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-6 py-2 rounded-lg shadow transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
            <span v-if="isSearching" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            {{ isSearching ? '搜尋中...' : '🔍 搜尋' }}
          </button>
        </div>

        <div v-if="searchResults.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[400px] overflow-y-auto pr-2">
          <div v-for="file in searchResults" :key="file.id" class="bg-white p-4 rounded-xl border border-indigo-100 shadow-sm flex flex-col hover:shadow-md transition-shadow">
            <h5 class="font-bold text-gray-800 break-all leading-tight mb-2">{{ file.filename }}</h5>
            <div class="flex items-center justify-between text-xs text-gray-500 mb-3">
              <span class="bg-gray-100 px-2 py-1 rounded">{{ file.size_mb }} MB</span>
              <span>{{ file.date }}</span>
            </div>
            <p v-if="file.caption" class="text-sm text-gray-600 mb-4 bg-gray-50 p-2 rounded truncate">{{ file.caption }}</p>
            <div v-else class="flex-1 mb-4"></div>
            
            <a :href="`https://lawxstudents168-tg-material-api.hf.space/download/${file.id}`" target="_blank" class="bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-2 rounded text-sm font-bold shadow-sm transition-colors text-center mt-auto">
              📥 立即串流下載
            </a>
          </div>
        </div>
        
        <div v-else-if="hasSearched" class="text-center py-6 text-gray-500 bg-white rounded-lg border border-dashed border-indigo-200">
          找不到符合的檔案。
        </div>
      </div>

      <div>
        <div class="flex justify-between items-center mb-3">
          <h4 class="font-bold text-teal-900 flex items-center">
            <span>☁️ 資料庫教材紀錄</span>
            <span class="ml-2 text-xs font-normal text-gray-500 border border-gray-200 px-2 py-1 rounded bg-gray-50">共 {{ tgMaterialsList.length }} 筆</span>
          </h4>
          <div class="flex gap-2">
            <input type="file" accept=".csv" ref="tgMaterialCsvInput" class="hidden" @change="handleMaterialCsvImport">
            <button @click="() => tgMaterialCsvInput.click()" class="text-xs bg-white border border-gray-300 text-gray-700 font-bold px-3 py-1.5 rounded shadow-sm hover:bg-gray-100 transition-colors">📥 匯入清單</button>
            <button @click="exportMaterialsCSV" class="text-xs bg-teal-600 text-white font-bold px-3 py-1.5 rounded shadow-sm hover:bg-teal-700 transition-colors">📤 匯出清單</button>
          </div>
        </div>
        
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
            <div v-else class="flex-1 mb-4"></div>

            <div class="flex flex-wrap gap-2 mt-auto border-t border-gray-100 pt-3">
              <a :href="getDownloadUrl(mat.url)" target="_blank" class="bg-teal-500 hover:bg-teal-600 text-white px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors text-center flex-1">
                📥 高速下載
              </a>
              <button @click="copyToClipboard(mat.url)" class="bg-gray-100 hover:bg-gray-200 text-gray-700 border border-gray-300 px-3 py-1.5 rounded text-xs font-bold shadow-sm transition-colors text-center flex-1">📋 複製 TG 連結</button>
            </div>
          </div>
          
          <div v-if="tgMaterialsList.length === 0" class="col-span-1 md:col-span-2 text-center py-10 text-gray-400 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50">
            目前雲端沒有任何教材紀錄。
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
  loadMaterials()
})

// ====== 🌟 下載連結轉換邏輯 ======
const getDownloadUrl = (url) => {
  if (!url) return '#'
  if (!url.includes('t.me/c/')) return url
  const parts = url.split('/')
  const messageId = parts[parts.length - 1]
  return `https://lawxstudents168-tg-material-api.hf.space/download/${messageId}`
}

// ====== 🔍 即時搜尋功能 (全新加入) ======
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const hasSearched = ref(false)

const searchCloudFiles = async () => {
  isSearching.value = true
  hasSearched.value = true
  try {
    const res = await fetch(`https://lawxstudents168-tg-material-api.hf.space/search?query=${encodeURIComponent(searchQuery.value)}&limit=20`)
    const data = await res.json()
    if (data.success) {
      searchResults.value = data.data
    } else {
      alert('搜尋失敗：' + data.error)
    }
  } catch (error) {
    alert('無法連線到搜尋伺服器')
  } finally {
    isSearching.value = false
  }
}

// ====== ⬆️ 上傳與資料庫歷史清單 ======
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
    
    let cap = `📚 教材：${file.name}\n上傳：${dayjs().format('YYYY/MM/DD HH:mm')}`; 
    if(tgMaterialCaption.value) cap += `\n📝 說明：${tgMaterialCaption.value}`; 
    fd.append('caption', cap)
    
    try {
      const res = await fetch('https://lawxstudents168-tg-material-api.hf.space/upload/', { method: 'POST', body: fd })
      if (!res.headers.get("content-type")?.includes("application/json")) throw new Error(`伺服器無回應或超時`)
      const data = await res.json()
      
      if (data.success) {
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
  materialUploadStatus.value = hasError ? (successCount ? '⚠️ 部分教材上傳失敗' : '❌ 上傳失敗 (可能檔案過大，建議使用 Go 傳輸工具)') : `✅ 成功上傳 ${successCount} 份教材！`
  loadMaterials()
}

const deleteMaterial = async (id) => {
  if(confirm('確定要從雲端紀錄移除此筆嗎？ (不會刪除 TG 實體檔案)')) {
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
</style>
