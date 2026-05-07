<template>
  <div class="fixed bottom-6 right-6 z-[100] flex flex-col items-end">
    <button 
      v-show="!isFullscreen"
      @click="toggleTrigger"
      class="w-14 h-14 bg-indigo-600 text-white rounded-full shadow-2xl flex items-center justify-center hover:scale-110 active:scale-95 transition-transform duration-200 z-10"
    >
      <span v-if="!isOpen" class="text-2xl">📝</span>
      <span v-else class="text-2xl">✖</span>
    </button>

    <div v-if="isOpen && !isVerified" class="mb-4 bg-white p-5 rounded-2xl shadow-2xl border border-gray-200 w-72 animate-fade-in relative z-10">
      <h4 class="font-bold text-gray-800 mb-3">請輸入編輯器密碼</h4>
      <input 
        v-model="inputPass" 
        type="password" 
        @keyup.enter="verifyPassword"
        placeholder="密碼..."
        class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-3"
      >
      <button @click="verifyPassword" class="w-full bg-gray-800 text-white py-2 rounded-lg text-sm font-bold">確認進入</button>
    </div>

    <div 
      v-if="isOpen && isVerified" 
      :class="[
        'bg-white shadow-2xl border border-gray-200 flex flex-col animate-fade-in overflow-hidden transition-all duration-300',
        isFullscreen ? 'fixed inset-0 w-full h-full z-[120] rounded-none' : 'mb-4 rounded-2xl w-[90vw] md:w-[600px] max-h-[80vh] relative z-10'
      ]"
    >
      <div class="bg-indigo-50 p-2 border-b border-indigo-100 flex flex-wrap items-center gap-2">
        <span class="text-indigo-800 font-bold ml-2 text-sm">📁 分類紀錄：</span>
        <select v-model="currentNoteId" @change="switchNote" class="border border-indigo-200 rounded p-1 text-sm bg-white font-bold text-gray-700 max-w-[150px] truncate focus:outline-none">
          <option v-for="note in notesList" :key="note.id" :value="note.id">{{ note.title }}</option>
        </select>
        
        <button @click="createNewNote" class="text-xs bg-white border border-indigo-200 text-indigo-700 px-2 py-1 rounded hover:bg-indigo-100 shadow-sm font-bold transition">➕ 新增</button>
        <button @click="deleteNote" class="text-xs bg-white border border-red-200 text-red-600 px-2 py-1 rounded hover:bg-red-50 shadow-sm font-bold transition">🗑️ 刪除</button>

        <div class="flex-1"></div>
        
        <button @click="toggleFullscreen" class="bg-gray-800 text-white px-3 py-1 rounded text-xs font-bold hover:bg-gray-700 transition flex items-center gap-1 shadow-sm mr-1">
          <span v-if="isFullscreen">🗗 縮回視窗</span>
          <span v-else>🗖 全螢幕放大</span>
        </button>
        <button v-if="isFullscreen" @click="toggleTrigger" class="bg-red-500 text-white px-3 py-1 rounded text-xs font-bold hover:bg-red-600 transition shadow-sm">
          ✖ 關閉
        </button>
      </div>

      <div class="bg-gray-50 p-2 border-b border-gray-200 flex flex-wrap items-center gap-1">
        <button @click="exec('bold')" class="p-1.5 hover:bg-gray-200 rounded font-bold w-8" title="粗體">B</button>
        <button @click="exec('italic')" class="p-1.5 hover:bg-gray-200 rounded italic w-8 font-serif" title="斜體">I</button>
        
        <button @click="exec('insertOrderedList')" class="p-1.5 hover:bg-gray-200 rounded font-bold flex items-center justify-center gap-1 px-2 border border-gray-200 bg-white shadow-sm ml-1" title="數字編號">
          <span class="text-[10px] leading-tight text-left">1.<br>2.</span>
          <span class="text-xs">編號</span>
        </button>

        <span class="text-gray-300 mx-1">|</span>

        <select @change="exec('fontSize', $event.target.value)" class="text-xs border border-gray-300 rounded p-1.5 bg-white shadow-sm focus:outline-none">
          <option value="3">中字體</option>
          <option value="1">小字體</option>
          <option value="5">大字體</option>
          <option value="7">特大字體</option>
        </select>
        
        <div class="flex items-center gap-1 ml-2 border border-gray-200 bg-white px-1 py-0.5 rounded shadow-sm">
          <span class="text-[10px] text-gray-500 font-bold ml-1">顏色</span>
          <input type="color" @input="exec('foreColor', $event.target.value)" class="w-6 h-6 p-0 border-0 bg-transparent cursor-pointer" title="文字顏色">
        </div>
        
        <div class="flex-1"></div>
        
        <button @click="saveContent" :disabled="isSaving" class="bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-green-700 disabled:opacity-50 transition shadow-sm flex items-center gap-1">
          <span v-if="isSaving" class="animate-spin w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
          {{ isSaving ? '儲存中...' : '💾 儲存並同步' }}
        </button>
      </div>

      <div 
        ref="editorRef"
        contenteditable="true" 
        :class="[
          'p-6 overflow-y-auto focus:outline-none prose max-w-none text-gray-800 leading-relaxed',
          isFullscreen ? 'flex-1 text-xl lg:text-2xl' : 'min-h-[300px] flex-1 text-sm'
        ]"
        @input="onInput"
      ></div>
      
      <div class="bg-gray-50 px-4 py-2 text-[10px] text-gray-400 flex justify-between border-t border-gray-200 mt-auto">
        <span>此內容與雲端同步，離開後需重新輸入密碼。</span>
        <span>上次更新：{{ lastUpdated }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
const supabase = useSupabaseClient()

const isOpen = ref(false)
const isVerified = ref(false)
const isFullscreen = ref(false)
const inputPass = ref('')
const editorRef = ref(null)
const isSaving = ref(false)
const lastUpdated = ref('--')

// 多檔筆記狀態
const notesList = ref([])
const currentNoteId = ref(null)

// 功能列執行命令
const exec = (command, value = null) => {
  document.execCommand(command, false, value)
  // 若使用清單或字體，強制讓編輯器保持焦點
  if (editorRef.value) editorRef.value.focus()
}

const toggleTrigger = () => {
  isOpen.value = !isOpen.value
  if (!isOpen.value) {
    isVerified.value = false // 關閉後重置驗證狀態
    isFullscreen.value = false // 關閉時退出全螢幕
    inputPass.value = ''
  }
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const verifyPassword = async () => {
  const { data } = await supabase.from('site_settings').select('editor_password').eq('id', 1).single()
  const correctPass = data?.editor_password || '590doc'
  
  if (inputPass.value === correctPass) {
    isVerified.value = true
    await loadNotes()
  } else {
    alert('密碼錯誤！')
  }
}

// 載入所有筆記分類
const loadNotes = async () => {
  const { data } = await supabase.from('system_scratchpad').select('*').order('updated_at', { ascending: false })
  
  if (data && data.length > 0) {
    notesList.value = data
    // 如果沒有選擇特定筆記，預設選擇第一筆
    if (!currentNoteId.value || !notesList.value.find(n => n.id === currentNoteId.value)) {
      currentNoteId.value = data[0].id
    }
  } else {
    // 如果資料庫全空，自動建立一個預設便籤
    await createNewNote(true, '預設便籤')
    return 
  }
  
  await renderCurrentNote()
}

// 切換筆記
const switchNote = async () => {
  await renderCurrentNote()
}

// 渲染當前筆記內容到編輯器
const renderCurrentNote = async () => {
  const currentNote = notesList.value.find(n => n.id === currentNoteId.value)
  if (currentNote) {
    lastUpdated.value = new Date(currentNote.updated_at).toLocaleString()
    await nextTick()
    if (editorRef.value) {
      editorRef.value.innerHTML = currentNote.content || ''
    }
  }
}

// 建立新筆記
const createNewNote = async (isAutoInit = false, autoTitle = '') => {
  let title = autoTitle
  if (!isAutoInit) {
    title = prompt('請輸入新分類的名稱：', '新紀錄')
    if (!title) return // 取消就不建立
  }

  const { data, error } = await supabase.from('system_scratchpad').insert([
    { title: title, content: '' }
  ]).select()

  if (data && data[0]) {
    currentNoteId.value = data[0].id
    await loadNotes()
  }
}

// 刪除筆記
const deleteNote = async () => {
  if (notesList.value.length <= 1) {
    alert('至少需要保留一份紀錄喔！您可以把內容清空即可。')
    return
  }
  if (confirm('確定要刪除這份紀錄嗎？')) {
    await supabase.from('system_scratchpad').delete().eq('id', currentNoteId.value)
    currentNoteId.value = null // 清空選擇，讓系統自動選第一筆
    await loadNotes()
  }
}

// 儲存內容
const saveContent = async () => {
  if (!currentNoteId.value) return
  isSaving.value = true
  const html = editorRef.value?.innerHTML || ''
  
  const { error } = await supabase.from('system_scratchpad').update({ 
    content: html,
    updated_at: new Date().toISOString()
  }).eq('id', currentNoteId.value)
  
  if (!error) {
    lastUpdated.value = new Date().toLocaleString()
    // 悄悄更新列表裡的狀態，避免切換時內容消失
    const noteIndex = notesList.value.findIndex(n => n.id === currentNoteId.value)
    if (noteIndex !== -1) notesList.value[noteIndex].content = html
  }
  isSaving.value = false
}

const onInput = () => {
  // 可以在此加入防抖動 (debounce) 的自動存檔邏輯
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }

/* 優化編輯器內的清單樣式 */
.prose ol {
  list-style-type: decimal;
  padding-left: 1.5rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.prose ul {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.prose li {
  margin-bottom: 0.25rem;
}
</style>
