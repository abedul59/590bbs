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
        <span class="text-indigo-800 font-bold ml-2 text-sm">📁 分類：</span>
        <select v-model="currentNoteId" @change="switchNote" class="border border-indigo-200 rounded p-1 text-sm bg-white font-bold text-gray-700 max-w-[120px] truncate focus:outline-none">
          <option v-for="note in notesList" :key="note.id" :value="note.id">{{ note.title }}</option>
        </select>
        
        <button @click="createNewNote" class="text-xs bg-white border border-indigo-200 text-indigo-700 px-2 py-1 rounded hover:bg-indigo-100 shadow-sm font-bold transition">➕</button>
        <button @click="deleteNote" class="text-xs bg-white border border-red-200 text-red-600 px-2 py-1 rounded hover:bg-red-50 shadow-sm font-bold transition">🗑️</button>

        <div class="flex-1"></div>
        
        <button @click="toggleFullscreen" class="bg-gray-800 text-white px-3 py-1 rounded text-xs font-bold hover:bg-gray-700 transition flex items-center gap-1 shadow-sm mr-1">
          <span v-if="isFullscreen">🗗 縮小</span>
          <span v-else>🗖 全螢幕放大</span>
        </button>
        <button v-if="isFullscreen" @click="toggleTrigger" class="bg-red-500 text-white px-3 py-1 rounded text-xs font-bold hover:bg-red-600 transition shadow-sm">✖ 關閉</button>
      </div>

      <div class="bg-gray-50 p-2 border-b border-gray-200 flex flex-wrap items-center gap-1">
        <button 
          @mousedown.prevent @click="exec('bold')" 
          :class="[activeStates.bold ? 'bg-gray-300 shadow-inner' : 'bg-white', 'p-1.5 rounded font-bold w-8 text-black border border-gray-200 shadow-sm']" 
          title="粗體">B</button>
          
        <button 
          @mousedown.prevent @click="exec('italic')" 
          :class="[activeStates.italic ? 'bg-gray-300 shadow-inner' : 'bg-white', 'p-1.5 rounded italic w-8 font-serif text-black border border-gray-200 shadow-sm']" 
          title="斜體">I</button>

        <span class="text-gray-300 mx-1">|</span>

        <button @mousedown.prevent @click="exec('justifyLeft')" :class="[activeStates.alignLeft ? 'bg-gray-300 shadow-inner' : 'bg-white', 'p-1.5 rounded border border-gray-200 shadow-sm']" title="靠左">⬅️</button>
        <button @mousedown.prevent @click="exec('justifyCenter')" :class="[activeStates.alignCenter ? 'bg-gray-300 shadow-inner' : 'bg-white', 'p-1.5 rounded border border-gray-200 shadow-sm']" title="置中">↔️</button>
        <button @mousedown.prevent @click="exec('justifyRight')" :class="[activeStates.alignRight ? 'bg-gray-300 shadow-inner' : 'bg-white', 'p-1.5 rounded border border-gray-200 shadow-sm']" title="靠右">➡️</button>

        <span class="text-gray-300 mx-1">|</span>

        <div class="flex items-center gap-1 bg-white border border-gray-200 rounded px-1.5 py-1 shadow-sm">
          <span class="text-[10px] font-bold text-gray-500">行距</span>
          <select @change="applyLineHeight($event.target.value)" class="text-xs focus:outline-none bg-transparent font-bold">
            <option value="1.5">1.5</option>
            <option value="1.0">1.0</option>
            <option value="1.2">1.2</option>
            <option value="2.0">2.0</option>
            <option value="2.5">2.5</option>
          </select>
        </div>

        <select @change="exec('fontSize', $event.target.value)" class="text-xs border border-gray-300 rounded p-1.5 bg-white shadow-sm focus:outline-none text-black">
          <option value="3">中字體</option>
          <option value="1">小字體</option>
          <option value="5">大字體</option>
          <option value="7">特大字體</option>
        </select>
        
        <div class="flex items-center gap-1 ml-2 border border-gray-200 bg-white px-1 py-0.5 rounded shadow-sm">
          <input type="color" @input="exec('foreColor', $event.target.value)" class="w-6 h-6 p-0 border-0 bg-transparent cursor-pointer" title="文字顏色">
        </div>
        
        <div class="flex-1"></div>
        
        <button @click="saveContent" :disabled="isSaving" class="bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-green-700 disabled:opacity-50 transition shadow-sm flex items-center gap-1">
          <span v-if="isSaving" class="animate-spin w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
          {{ isSaving ? '儲存同步' : '💾 儲存' }}
        </button>
      </div>

      <div 
        ref="editorRef"
        contenteditable="true" 
        :class="[
          'p-6 overflow-y-auto focus:outline-none prose max-w-none text-gray-800 editor-content',
          isFullscreen ? 'flex-1 text-xl lg:text-2xl' : 'min-h-[300px] flex-1 text-sm'
        ]"
        @input="onInput"
        @keyup="checkFormatting"
        @mouseup="checkFormatting"
      ></div>
      
      <div class="bg-gray-50 px-4 py-2 text-[10px] text-gray-400 flex justify-between border-t border-gray-200 mt-auto">
        <span>此內容與雲端同步。</span>
        <span>上次更新：{{ lastUpdated }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const supabase = useSupabaseClient()

const isOpen = ref(false)
const isVerified = ref(false)
const isFullscreen = ref(false)
const inputPass = ref('')
const editorRef = ref(null)
const isSaving = ref(false)
const lastUpdated = ref('--')

const notesList = ref([])
const currentNoteId = ref(null)

const activeStates = ref({
  bold: false,
  italic: false,
  alignLeft: false,
  alignCenter: false,
  alignRight: false
})

const checkFormatting = () => {
  if (!editorRef.value) return
  activeStates.value.bold = document.queryCommandState('bold')
  activeStates.value.italic = document.queryCommandState('italic')
  activeStates.value.alignLeft = document.queryCommandState('justifyLeft')
  activeStates.value.alignCenter = document.queryCommandState('justifyCenter')
  activeStates.value.alignRight = document.queryCommandState('justifyRight')
}

const exec = (command, value = null) => {
  editorRef.value.focus()
  document.execCommand(command, false, value)
  checkFormatting()
}

// 🌟 行距處理邏輯
const applyLineHeight = (value) => {
  editorRef.value.focus()
  // 取得目前選取的節點
  const selection = window.getSelection()
  if (selection.rangeCount > 0) {
    const range = selection.getRangeAt(0)
    let container = range.commonAncestorContainer
    if (container.nodeType === 3) container = container.parentNode
    
    // 尋找最近的區塊元素 (如 div, p) 或直接套用在編輯器容器上
    const block = container.closest('div, p') || editorRef.value
    block.style.lineHeight = value
  }
}

const toggleTrigger = () => {
  isOpen.value = !isOpen.value
  if (!isOpen.value) {
    isVerified.value = false
    isFullscreen.value = false
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

const loadNotes = async () => {
  const { data } = await supabase.from('system_scratchpad').select('*').order('updated_at', { ascending: false })
  
  if (data && data.length > 0) {
    notesList.value = data
    if (!currentNoteId.value || !notesList.value.find(n => n.id === currentNoteId.value)) {
      currentNoteId.value = data[0].id
    }
  } else {
    await createNewNote(true, '預設便籤')
    return 
  }
  await renderCurrentNote()
}

const switchNote = async () => {
  await renderCurrentNote()
}

const renderCurrentNote = async () => {
  const currentNote = notesList.value.find(n => n.id === currentNoteId.value)
  if (currentNote) {
    lastUpdated.value = new Date(currentNote.updated_at).toLocaleString()
    await nextTick()
    if (editorRef.value) {
      editorRef.value.innerHTML = currentNote.content || ''
      checkFormatting()
    }
  }
}

const createNewNote = async (isAutoInit = false, autoTitle = '') => {
  let title = autoTitle
  if (!isAutoInit) {
    title = prompt('請輸入新紀錄名稱：', '新紀錄')
    if (!title) return
  }

  const { data } = await supabase.from('system_scratchpad').insert([
    { title: title, content: '' }
  ]).select()

  if (data && data[0]) {
    currentNoteId.value = data[0].id
    await loadNotes()
  }
}

const deleteNote = async () => {
  if (notesList.value.length <= 1) return alert('需保留至少一份紀錄。')
  if (confirm('確定刪除？')) {
    await supabase.from('system_scratchpad').delete().eq('id', currentNoteId.value)
    currentNoteId.value = null
    await loadNotes()
  }
}

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
    const noteIndex = notesList.value.findIndex(n => n.id === currentNoteId.value)
    if (noteIndex !== -1) notesList.value[noteIndex].content = html
  }
  isSaving.value = false
}

const onInput = () => {
  checkFormatting()
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }

/* 🌟 核心樣式強化：確保行距與對齊生效 */
.editor-content {
  line-height: 1.5; /* 預設行距 */
}
.editor-content b, .editor-content strong {
  font-weight: 900 !important;
}
.editor-content i, .editor-content em {
  font-style: italic !important;
}
.editor-content div, .editor-content p {
  margin-bottom: 0.5rem;
}
</style>
