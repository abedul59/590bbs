<template>
  <div class="space-y-8 animate-fade-in">
    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 class="text-xl font-semibold mb-4 flex items-center gap-2">
        🔒 後台專屬私密分頁 
        <span class="text-xs bg-gray-800 text-white px-2 py-1 rounded shadow-sm">僅限管理員可見</span>
      </h3>

      <div class="flex flex-wrap items-center gap-2 mb-6 bg-gray-50 p-2 rounded-lg border border-gray-200 min-h-[56px]">
        <div v-for="tab in adminTabs" :key="tab.id" class="relative group flex items-center">
          <div v-if="editingTabId === tab.id" class="flex items-center bg-white border-2 border-blue-400 rounded-full px-2 py-1 shadow-sm">
            <input v-model="editingTabName" @keyup.enter="saveTabName(tab)" class="w-24 text-sm outline-none px-1">
            <button @click="saveTabName(tab)" class="text-green-600 hover:bg-green-100 p-1 rounded-full text-xs">✔</button>
            <button @click="editingTabId = null" class="text-red-500 hover:bg-red-100 p-1 rounded-full text-xs">✖</button>
          </div>
          <button v-else @click="activeAdminTab = tab.id" :class="[activeAdminTab === tab.id ? 'bg-blue-600 text-white shadow-md' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100', 'px-4 py-2 rounded-full font-bold text-sm transition-all flex items-center gap-1.5']">
            {{ tab.name }}
            <span @click.stop="startEditTab(tab)" class="text-[10px] opacity-0 group-hover:opacity-100 hover:text-blue-300 transition-opacity ml-1 bg-black/10 px-1.5 py-0.5 rounded">✎</span>
            <span @click.stop="deleteAdminTab(tab.id)" class="text-[10px] opacity-0 group-hover:opacity-100 hover:text-red-400 transition-opacity bg-black/10 px-1.5 py-0.5 rounded">✖</span>
          </button>
        </div>
        
        <div class="flex items-center ml-auto bg-white border border-gray-300 rounded-full overflow-hidden shadow-sm">
          <input v-model="newAdminTabName" type="text" placeholder="+ 新增分頁" class="text-sm px-3 py-2 w-28 md:w-32 focus:outline-none" @keyup.enter="addAdminTab">
          <button @click="addAdminTab" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 text-sm font-bold transition-colors border-l border-gray-300">新增</button>
        </div>
      </div>

      <div v-if="activeAdminTab" class="bg-blue-50 border border-blue-100 p-4 rounded-xl relative">
        <div class="flex flex-col md:flex-row md:justify-between md:items-center border-b border-blue-200 pb-3 mb-4 gap-3">
          <h4 class="font-bold text-blue-800 flex items-center gap-2">📝 在「{{ currentTabName }}」新增私密內容</h4>
          
          <input type="file" accept=".csv" ref="csvFileInput" class="hidden" @change="handleCsvImport">
          <div class="flex gap-2">
            <button @click="triggerImportCsv" class="text-xs bg-white border border-gray-300 text-gray-700 hover:bg-gray-100 font-bold px-3 py-1.5 rounded shadow-sm">📥 匯入 CSV</button>
            <button @click="exportAdminNotesCSV" class="text-xs bg-green-600 text-white hover:bg-green-700 font-bold px-3 py-1.5 rounded shadow-sm">📤 匯出 CSV</button>
          </div>
        </div>

        <div v-if="editingAdminNote" class="bg-white p-4 rounded-lg shadow-sm border border-yellow-300 mb-4 ring-2 ring-yellow-200">
          <h5 class="text-xs font-bold text-yellow-600 mb-2">✏️ 編輯模式中</h5>
          <input v-model="editingAdminNote.title" type="text" placeholder="標題 (必填)" class="border border-gray-300 p-2 w-full rounded text-sm mb-2 focus:ring-2 focus:ring-blue-400 outline-none">
          <textarea v-model="editingAdminNote.description" placeholder="內容說明..." class="border border-gray-300 p-2 w-full rounded text-sm mb-2 rows-2 focus:ring-2 focus:ring-blue-400 outline-none"></textarea>
          <input v-model="editingAdminNote.url" type="url" placeholder="主要網址 (選填)" class="border border-gray-300 p-2 w-full rounded text-sm mb-2 focus:ring-2 focus:ring-blue-400 outline-none">
          
          <div class="flex gap-4 mb-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="editingAdminNote.is_pinned" type="checkbox" class="w-4 h-4 rounded text-blue-600">
              <span class="text-xs font-bold text-yellow-600">📌 置頂</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="editingAdminNote.is_important" type="checkbox" class="w-4 h-4 rounded text-red-600">
              <span class="text-xs font-bold text-red-600">🔥 重要</span>
            </label>
          </div>
          
          <div class="bg-gray-50 p-2 rounded mb-2 border border-gray-200">
            <div class="flex justify-between items-center mb-1">
              <span class="text-xs text-gray-500 font-bold">額外網址</span>
              <button @click="addLinkToObj(editingAdminNote)" class="text-[10px] bg-gray-200 hover:bg-gray-300 px-2 py-0.5 rounded font-bold">+ 新增</button>
            </div>
            <div v-for="(link, index) in editingAdminNote.links" :key="index" class="flex gap-1 mb-1 items-center">
              <input v-model="link.name" type="text" placeholder="名稱" class="border border-gray-300 p-1 text-xs rounded w-1/3">
              <input v-model="link.url" type="url" placeholder="網址" class="border border-gray-300 p-1 text-xs rounded flex-1">
              <button @click="removeLinkFromObj(editingAdminNote, index)" class="text-red-500 hover:bg-red-100 text-xs px-1.5 py-0.5 rounded">✖</button>
            </div>
          </div>
          
          <div class="flex justify-end gap-2">
            <button @click="cancelEditAdminNote" class="text-xs px-3 py-1.5 bg-gray-200 rounded hover:bg-gray-300 font-bold">取消</button>
            <button @click="saveAdminNote" class="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 font-bold">儲存變更</button>
          </div>
        </div>

        <div v-else class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
          <input v-model="newAdminNote.title" type="text" placeholder="標題 (必填)" class="border border-gray-300 p-2 w-full rounded text-sm focus:ring-2 focus:ring-blue-400 outline-none mb-2">
          <textarea v-model="newAdminNote.description" placeholder="內容說明..." class="border border-gray-300 p-2 w-full rounded text-sm mb-2 focus:ring-2 focus:ring-blue-400 outline-none rows-3"></textarea>
          <input v-model="newAdminNote.url" type="url" placeholder="主要網址 (選填)" class="border border-gray-300 p-2 w-full rounded text-sm mb-3 focus:ring-2 focus:ring-blue-400 outline-none bg-gray-50">
          
          <div class="bg-gray-50 p-2 rounded mb-3 border border-gray-200">
            <div class="flex justify-between items-center mb-1">
              <span class="text-xs text-gray-500 font-bold">額外相關網址 (選填)</span>
              <button @click="addLinkToObj(newAdminNote)" class="text-[10px] bg-gray-200 hover:bg-gray-300 px-2 py-0.5 rounded font-bold">+ 新增網址</button>
            </div>
            <div v-for="(link, index) in newAdminNote.links" :key="index" class="flex gap-1 mb-1 items-center">
              <input v-model="link.name" type="text" placeholder="按鈕名稱" class="border border-gray-300 p-1.5 text-xs rounded w-1/3">
              <input v-model="link.url" type="url" placeholder="https://..." class="border border-gray-300 p-1.5 text-xs rounded flex-1">
              <button @click="removeLinkFromObj(newAdminNote, index)" class="text-red-500 hover:bg-red-100 text-xs px-2 py-1 rounded">✖</button>
            </div>
          </div>

          <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div class="flex gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="newAdminNote.is_pinned" type="checkbox" class="w-4 h-4 text-blue-600 rounded">
                <span class="text-xs font-bold text-yellow-600">📌 置頂</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="newAdminNote.is_important" type="checkbox" class="w-4 h-4 text-red-600 rounded">
                <span class="text-xs font-bold text-red-600">🔥 重要</span>
              </label>
            </div>
            <button @click="addAdminNote" class="bg-gray-800 text-white px-5 py-2 rounded text-sm font-bold shadow hover:bg-gray-900 transition">💾 新增私密紀錄</button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="item in filteredAdminNotes" :key="item.id" :class="['relative p-5 rounded-xl shadow-sm hover:shadow-md transition duration-300 flex flex-col', item.is_important ? 'bg-red-50 border border-red-300' : 'bg-white border border-gray-200']">
            
            <div class="absolute -top-3 -right-2 flex gap-1">
              <span v-if="item.is_pinned" class="bg-yellow-400 text-white text-[10px] font-bold px-2 py-1 rounded-full shadow">📌 置頂</span>
              <span v-if="item.is_important" class="bg-red-500 text-white text-[10px] font-bold px-2 py-1 rounded-full shadow">🔥 重要</span>
            </div>
            
            <div class="text-[10px] text-gray-400 mb-2 flex justify-between items-center font-mono">
              <span>🕒 {{ formatDate(item.created_at) }}</span>
              <div class="flex gap-2">
                <button @click="startEditAdminNote(item)" class="text-blue-500 hover:text-blue-700 underline font-bold px-1">編輯</button>
                <button @click="deleteAdminNote(item.id)" class="text-red-500 hover:text-red-700 underline font-bold px-1">刪除</button>
              </div>
            </div>
            
            <h5 :class="['text-lg font-bold mb-1', item.is_important ? 'text-red-700' : 'text-gray-900']">{{ item.title }}</h5>
            <p class="text-sm text-gray-600 whitespace-pre-wrap flex-1">{{ item.description }}</p>
            
            <div class="mt-3 flex flex-wrap gap-2">
              <a v-if="item.url" :href="item.url" target="_blank" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-sm hover:bg-blue-700 transition-colors">主要網址 🚀</a>
              <a v-for="(link, index) in item.links || []" :key="index" :href="link.url" target="_blank" class="bg-gray-100 border border-gray-300 text-gray-700 hover:bg-gray-200 px-3 py-1.5 rounded-lg text-xs font-bold shadow-sm transition-colors">{{ link.name || '參考網址' }}</a>
            </div>
          </div>
          
          <div v-if="filteredAdminNotes.length === 0" class="col-span-1 md:col-span-2 text-center py-10 text-gray-400 border-2 border-dashed border-gray-300 rounded-xl bg-white opacity-60">
            這個分頁目前沒有任何私密紀錄。
          </div>
        </div>
      </div>

      <div v-else class="text-center py-6 text-gray-400 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50">
        👆 請在上方選擇或新增一個分頁。
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const supabase = useSupabaseClient()
const dayjs = useDayjs()

// ====== 共用 CSV 解析函數 ======
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

const formatDate = (dateString) => dayjs(dateString).format('YYYY/MM/DD HH:mm')

// ====== 私密分頁變數 ======
const adminTabs = ref([])
const activeAdminTab = ref(null)
const newAdminTabName = ref('')
const editingTabId = ref(null)     
const editingTabName = ref('')     

const currentTabName = computed(() => adminTabs.value.find(t => t.id === activeAdminTab.value)?.name || '')

const adminNotes = ref([])
const getEmptyAdminNote = () => ({ title: '', description: '', url: '', is_important: false, is_pinned: false, links: [] })
const newAdminNote = ref(getEmptyAdminNote())
const editingAdminNote = ref(null)

const filteredAdminNotes = computed(() => {
  if (!activeAdminTab.value || !adminNotes.value) return []
  return adminNotes.value
    .filter(n => n.tab_id === activeAdminTab.value)
    .sort((a, b) => {
      if (a.is_pinned !== b.is_pinned) return a.is_pinned ? -1 : 1
      return new Date(b.created_at) - new Date(a.created_at)
    })
})

onMounted(() => {
  loadAdminTabs()
  loadAdminNotes()
})

// ====== 私密分頁邏輯 ======
const loadAdminTabs = async () => {
  const { data } = await supabase.from('admin_tabs').select('*').order('created_at', { ascending: true })
  if (data) {
    adminTabs.value = data
    if (data.length > 0 && !activeAdminTab.value) activeAdminTab.value = data[0].id
  }
}

const addAdminTab = async () => {
  if (!newAdminTabName.value) return alert('請輸入分頁名稱')
  const { data, error } = await supabase.from('admin_tabs').insert([{ name: newAdminTabName.value }]).select().single()
  if (!error && data) {
    newAdminTabName.value = ''
    await loadAdminTabs()
    activeAdminTab.value = data.id
  }
}

const deleteAdminTab = async (id) => {
  if (!confirm('確定刪除此分頁？這會同時刪除裡面「所有」的內容喔！')) return
  await supabase.from('admin_tabs').delete().eq('id', id)
  if (activeAdminTab.value === id) activeAdminTab.value = null
  loadAdminTabs()
  loadAdminNotes()
}

const startEditTab = (tab) => {
  editingTabId.value = tab.id
  editingTabName.value = tab.name
}

const saveTabName = async (tab) => {
  if (!editingTabName.value) return alert('名稱不能為空！')
  const { error } = await supabase.from('admin_tabs').update({ name: editingTabName.value }).eq('id', tab.id)
  if (!error) {
    editingTabId.value = null
    loadAdminTabs()
  } else alert('更新失敗')
}

// ====== 私密內容邏輯 ======
const loadAdminNotes = async () => {
  const { data } = await supabase.from('admin_notes').select('*')
  if (data) adminNotes.value = data
}

const addAdminNote = async () => {
  if (!newAdminNote.value.title) return alert('標題為必填！')
  await supabase.from('admin_notes').insert([{ ...newAdminNote.value, tab_id: activeAdminTab.value }])
  newAdminNote.value = getEmptyAdminNote()
  loadAdminNotes()
}

const deleteAdminNote = async (id) => {
  if (!confirm('確定刪除此紀錄？')) return
  await supabase.from('admin_notes').delete().eq('id', id)
  loadAdminNotes()
}

const startEditAdminNote = (note) => {
  editingAdminNote.value = JSON.parse(JSON.stringify({ ...note, links: note.links || [] }))
}
const cancelEditAdminNote = () => { editingAdminNote.value = null }

const saveAdminNote = async () => {
  if (!editingAdminNote.value.title) return alert('標題必填！')
  const { id, title, description, url, links, is_important, is_pinned } = editingAdminNote.value
  await supabase.from('admin_notes').update({ title, description, url, links, is_important, is_pinned }).eq('id', id)
  editingAdminNote.value = null
  loadAdminNotes()
}

const addLinkToObj = (obj) => {
  if (!obj.links) obj.links = []
  obj.links.push({ name: '', url: '' })
}
const removeLinkFromObj = (obj, index) => { obj.links.splice(index, 1) }

// ====== 私密內容匯出與匯入 CSV ======
const exportAdminNotesCSV = () => {
  const notes = filteredAdminNotes.value
  if (!notes.length) return alert('這個分頁目前沒有資料可以匯出喔！')
  
  const headers = ['標題(title)', '內容說明(description)', '主網址(url)', '是否置頂(is_pinned)', '是否重要(is_important)', '額外網址(links_json)']
  let csvContent = headers.join(',') + '\n'
  
  notes.forEach(n => {
    const title = `"${(n.title || '').replace(/"/g, '""')}"`
    const desc = `"${(n.description || '').replace(/"/g, '""')}"`
    const url = `"${(n.url || '').replace(/"/g, '""')}"`
    const isPinned = n.is_pinned ? 'TRUE' : 'FALSE'
    const isImportant = n.is_important ? 'TRUE' : 'FALSE'
    const linksStr = `"${JSON.stringify(n.links || []).replace(/"/g, '""')}"`
    csvContent += [title, desc, url, isPinned, isImportant, linksStr].join(',') + '\n'
  })
  
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `私密分頁備份_${currentTabName.value}.csv`
  link.click()
}

const csvFileInput = ref(null)
const triggerImportCsv = () => { csvFileInput.value.click() }

const handleCsvImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = async (e) => {
    const text = e.target.result
    const rows = parseCSVString(text)
    
    if (rows.length < 2) return alert('CSV 檔案格式錯誤或沒有資料！')
    
    const insertData = []
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i]
      if (row.length < 6) continue 
      
      let parsedLinks = []
      try { parsedLinks = JSON.parse(row[5]) } catch(e) {}

      insertData.push({
        tab_id: activeAdminTab.value,
        title: row[0],
        description: row[1],
        url: row[2],
        is_pinned: row[3].trim().toUpperCase() === 'TRUE',
        is_important: row[4].trim().toUpperCase() === 'TRUE',
        links: parsedLinks
      })
    }
    
    if (insertData.length > 0) {
      const { error } = await supabase.from('admin_notes').insert(insertData)
      if (error) alert('匯入失敗: ' + error.message)
      else {
        alert(`成功匯入 ${insertData.length} 筆資料！`)
        loadAdminNotes()
      }
    }
    csvFileInput.value.value = '' 
  }
  reader.readAsText(file)
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>