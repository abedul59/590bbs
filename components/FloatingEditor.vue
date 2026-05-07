<template>
  <div class="fixed bottom-6 right-6 z-[100] flex flex-col items-end">
    <button 
      @click="toggleTrigger"
      class="w-14 h-14 bg-indigo-600 text-white rounded-full shadow-2xl flex items-center justify-center hover:scale-110 active:scale-95 transition-transform duration-200"
    >
      <span v-if="!isOpen" class="text-2xl">📝</span>
      <span v-else class="text-2xl">✖</span>
    </button>

    <div v-if="isOpen && !isVerified" class="mb-4 bg-white p-5 rounded-2xl shadow-2xl border border-gray-200 w-72 animate-fade-in">
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

    <div v-if="isOpen && isVerified" class="mb-4 bg-white rounded-2xl shadow-2xl border border-gray-200 w-[90vw] md:w-[600px] flex flex-col animate-fade-in overflow-hidden">
      <div class="bg-gray-50 p-2 border-b border-gray-200 flex flex-wrap items-center gap-1">
        <button @click="exec('bold')" class="p-1.5 hover:bg-gray-200 rounded font-bold w-8" title="粗體">B</button>
        <button @click="exec('italic')" class="p-1.5 hover:bg-gray-200 rounded italic w-8" title="斜體">I</button>
        <select @change="exec('fontSize', $event.target.value)" class="text-xs border border-gray-300 rounded p-1 bg-white">
          <option value="3">中字體</option>
          <option value="1">小字體</option>
          <option value="5">大字體</option>
          <option value="7">特大字體</option>
        </select>
        <input type="color" @input="exec('foreColor', $event.target.value)" class="w-8 h-8 p-0 border-0 bg-transparent cursor-pointer" title="文字顏色">
        
        <div class="flex-1"></div>
        
        <button @click="saveContent" :disabled="isSaving" class="bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-green-700 disabled:opacity-50 transition">
          {{ isSaving ? '儲存中...' : '💾 儲存並同步' }}
        </button>
        <button @click="clearContent" class="text-gray-400 hover:text-red-500 p-1.5" title="清空內容">🗑️</button>
      </div>

      <div 
        ref="editorRef"
        contenteditable="true" 
        class="p-6 min-h-[300px] max-h-[60vh] overflow-y-auto focus:outline-none prose prose-sm max-w-none text-gray-800"
        @input="onInput"
      ></div>
      
      <div class="bg-gray-50 px-4 py-2 text-[10px] text-gray-400 flex justify-between">
        <span>此內容與雲端同步，離開後需重新輸入密碼。</span>
        <span>上次更新：{{ lastUpdated }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const supabase = useSupabaseClient()

const isOpen = ref(false)
const isVerified = ref(false)
const inputPass = ref('')
const editorRef = ref(null)
const isSaving = ref(false)
const lastUpdated = ref('--')
const contentHtml = ref('')

// 功能列執行命令
const exec = (command, value = null) => {
  document.execCommand(command, false, value)
}

const toggleTrigger = () => {
  isOpen.value = !isOpen.value
  if (!isOpen.value) {
    isVerified.value = false // 關閉後重置驗證狀態
    inputPass.value = ''
  }
}

const verifyPassword = async () => {
  const { data } = await supabase.from('site_settings').select('editor_password').eq('id', 1).single()
  const correctPass = data?.editor_password || '590doc'
  
  if (inputPass.value === correctPass) {
    isVerified.value = true
    await loadContent()
  } else {
    alert('密碼錯誤！')
  }
}

const loadContent = async () => {
  const { data } = await supabase.from('system_scratchpad').select('*').eq('id', 1).single()
  if (data) {
    contentHtml.value = data.content || ''
    lastUpdated.value = new Date(data.updated_at).toLocaleString()
    // 確保組件渲染後才填入內容
    setTimeout(() => {
      if (editorRef.value) editorRef.value.innerHTML = contentHtml.value
    }, 50)
  }
}

const saveContent = async () => {
  isSaving.value = true
  const html = editorRef.value?.innerHTML || ''
  const { error } = await supabase.from('system_scratchpad').update({ 
    content: html,
    updated_at: new Date().toISOString()
  }).eq('id', 1)
  
  if (!error) {
    lastUpdated.value = new Date().toLocaleString()
  }
  isSaving.value = false
}

const clearContent = () => {
  if (confirm('確定要清空所有內容嗎？')) {
    if (editorRef.value) editorRef.value.innerHTML = ''
  }
}

const onInput = () => {
  // 可以增加自動存檔邏輯
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
