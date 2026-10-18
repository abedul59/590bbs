<template>
  <div class="space-y-8 animate-fade-in">

    <nav class="bg-white p-2 rounded-xl shadow-sm border border-gray-100 flex flex-wrap gap-2" aria-label="前台公告與暫存分類">
      <button
        type="button"
        @click="activePublicTab = 'todos'"
        :class="activePublicTab === 'todos' ? [themeObj.bg, 'text-white'] : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
        class="px-4 py-2 rounded-lg text-sm font-bold transition-colors"
      >📝 暫存清單</button>
      <button
        v-for="cat in categories"
        :key="cat.id"
        type="button"
        @click="selectCategoryTab(cat.name)"
        :class="activePublicTab === cat.name ? [themeObj.bg, 'text-white'] : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
        class="px-4 py-2 rounded-lg text-sm font-bold transition-colors"
      >{{ cat.icon }} {{ cat.name }}</button>
    </nav>
    
    <section v-if="activePublicTab === 'todos'" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div class="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-3">
        <h3 class="text-xl font-semibold flex items-center gap-2">
          📝 管理員暫存清單 
          <span class="text-xs text-gray-400 font-normal border px-2 py-1 rounded">一般事務</span>
        </h3>
        <div class="flex gap-2">
          <input type="file" accept=".csv" ref="todoCsvInput" class="hidden" @change="handleTodoCsvImport">
          <button @click="() => todoCsvInput.click()" class="text-xs bg-white border border-gray-300 text-gray-700 hover:bg-gray-100 font-bold px-3 py-1.5 rounded shadow-sm transition">📥 匯入 CSV</button>
          <button @click="exportTodosCSV" class="text-xs bg-gray-800 text-white hover:bg-gray-900 font-bold px-3 py-1.5 rounded shadow-sm transition">📤 匯出 CSV</button>
        </div>
      </div>

      <div class="flex flex-col md:flex-row gap-2 mb-4 bg-gray-50 p-3 rounded-lg border border-gray-200">
        <input v-model="newTodo.content" type="text" placeholder="輸入備忘、草稿或代辦事項..." :class="['border border-gray-300 p-2 flex-[2] rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
        <input v-model="newTodo.url" type="url" placeholder="附加網址 (選填)" :class="['border border-gray-300 p-2 flex-1 rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
        <input v-model="newTodo.due_date" type="datetime-local" title="指定日期時間 (選填)" :class="['border border-gray-300 p-2 rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent text-gray-600', themeObj.ring]">
        <button @click="addTodo" class="bg-gray-800 text-white px-5 py-2 rounded hover:bg-gray-900 text-sm font-medium whitespace-nowrap transition-colors">新增紀錄</button>
      </div>

      <ul class="space-y-2 max-h-[300px] overflow-y-auto pr-2">
        <li v-for="todo in todosList" :key="todo.id" :class="['flex justify-between items-center p-3 rounded-lg border transition-all duration-200', todo.is_completed ? 'bg-gray-100 border-gray-200 opacity-60' : 'bg-white border-gray-300 shadow-sm']">
          <div class="flex items-center gap-3 overflow-hidden">
            <input type="checkbox" :checked="todo.is_completed" @change="toggleTodo(todo)" :class="['w-5 h-5 rounded cursor-pointer', themeObj.text]">
            <div class="flex flex-col">
              <span :class="['font-medium text-gray-800 truncate', {'line-through text-gray-500': todo.is_completed}]">{{ todo.content }}</span>
              <div class="flex gap-3 text-xs text-gray-500 mt-1">
                <span v-if="todo.due_date" class="bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded flex items-center gap-1">⏰ {{ formatTodoDate(todo.due_date) }}</span>
                <a v-if="todo.url" :href="todo.url" target="_blank" class="text-blue-500 hover:underline truncate max-w-[150px]">🔗 相關連結</a>
                <span class="text-gray-400">建立於: {{ formatDate(todo.created_at) }}</span>
              </div>
            </div>
          </div>
          <button @click="deleteTodo(todo.id)" class="text-gray-400 hover:text-red-500 hover:bg-red-50 p-1.5 rounded transition-colors">✖</button>
        </li>
        <li v-if="todosList.length === 0" class="text-sm text-gray-400 py-4 text-center bg-gray-50 rounded-lg border border-dashed border-gray-300">目前沒有任何待辦或暫存訊息。</li>
      </ul>
    </section>

    <section v-else class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <h3 class="text-xl font-semibold">📢 {{ activePublicTab }}公告</h3>
        <label class="flex items-center gap-2 text-sm text-gray-600">
          排列方式
          <select v-model="postSort" class="border border-gray-300 rounded-lg bg-white px-3 py-2 text-sm">
            <option value="newest">日期：最新優先</option>
            <option value="oldest">日期：最早優先</option>
            <option value="important">重要性優先</option>
          </select>
        </label>
      </div>
      
      <div class="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-6">
        <h4 class="font-bold text-gray-700 mb-3">✨ 發布新公告到前台</h4>
        <div class="space-y-4">
          <div class="flex flex-col md:flex-row gap-3">
            <div class="md:w-1/3">
              <label class="block text-sm text-gray-600 mb-1">所屬科目</label>
              <select v-model="newPost.category" :class="['border border-gray-300 p-2 w-full rounded bg-white focus:ring-2 focus:border-transparent focus:outline-none', themeObj.ring]">
                <option v-for="cat in categories" :key="cat.id" :value="cat.name">{{ cat.icon }} {{ cat.name }}</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm text-gray-600 mb-1">教學標題 (必填)</label>
              <input v-model="newPost.title" type="text" placeholder="輸入標題..." :class="['border border-gray-300 p-2 w-full rounded focus:ring-2 focus:border-transparent focus:outline-none', themeObj.ring]">
            </div>
          </div>
          
          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer"><input v-model="newPost.is_pinned" type="checkbox" class="w-4 h-4 text-blue-600 rounded"><span class="text-sm font-bold text-yellow-600">📌 置頂此公告</span></label>
            <label class="flex items-center gap-2 cursor-pointer"><input v-model="newPost.is_important" type="checkbox" class="w-4 h-4 text-red-600 rounded"><span class="text-sm font-bold text-red-600">🔥 標記為重要</span></label>
          </div>

          <div>
            <label class="block text-sm text-gray-600 mb-1">內容說明</label>
            <textarea v-model="newPost.description" placeholder="簡單描述一下..." :class="['border border-gray-300 p-2 w-full rounded focus:ring-2 focus:border-transparent focus:outline-none rows-2', themeObj.ring]"></textarea>
          </div>
          
          <div>
            <label class="block text-sm text-gray-600 mb-1">主要網址 (必填)</label>
            <input v-model="newPost.url" type="url" placeholder="https://..." :class="['border border-gray-300 p-2 w-full rounded focus:ring-2 focus:border-transparent focus:outline-none', themeObj.ring]">
          </div>

          <div class="bg-white p-3 rounded border border-gray-200">
            <div class="flex justify-between items-center mb-2">
              <label class="text-sm text-gray-600 font-bold">額外相關網址 (選填)</label>
              <button @click="addLinkToObj(newPost)" class="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded hover:bg-blue-200">+ 新增網址</button>
            </div>
            <div v-for="(link, index) in newPost.links" :key="index" class="flex gap-2 mb-2 items-center">
              <input v-model="link.name" type="text" placeholder="按鈕名稱" class="border border-gray-300 p-1.5 text-sm rounded w-1/3">
              <input v-model="link.url" type="url" placeholder="https://..." class="border border-gray-300 p-1.5 text-sm rounded flex-1">
              <button @click="removeLinkFromObj(newPost, index)" class="text-red-500 hover:text-red-700 font-bold px-2">✖</button>
            </div>
          </div>

          <button @click="addPost" :class="[themeObj.bg, themeObj.hover, 'text-white px-6 py-2 rounded font-medium transition duration-300 shadow-sm w-full md:w-auto']">發布內容</button>
        </div>
      </div>

      <div v-if="editingPost" class="bg-yellow-50 p-4 rounded-xl border border-yellow-200 shadow-sm space-y-4 mb-4 animate-fade-in relative">
        <div class="flex justify-between items-center border-b border-yellow-200 pb-2">
          <h4 class="font-bold text-gray-800">✏️ 編輯前台教學內容</h4>
          <button @click="cancelEdit" class="text-gray-500 hover:text-red-500 text-sm font-bold">✖ 取消</button>
        </div>
        
        <div class="flex flex-col md:flex-row gap-3">
          <div class="md:w-1/3">
            <label class="block text-xs text-gray-500 mb-1">分類</label>
            <select v-model="editingPost.category" class="border border-gray-300 p-2 w-full rounded bg-white text-sm">
              <option v-for="cat in categories" :key="cat.id" :value="cat.name">{{ cat.icon }} {{ cat.name }}</option>
            </select>
          </div>
          <div class="flex-1">
            <label class="block text-xs text-gray-500 mb-1">標題</label>
            <input v-model="editingPost.title" type="text" class="border border-gray-300 p-2 w-full rounded text-sm">
          </div>
        </div>

        <div class="flex gap-4">
          <label class="flex items-center gap-2 cursor-pointer"><input v-model="editingPost.is_pinned" type="checkbox" class="w-4 h-4 text-blue-600 rounded"><span class="text-sm font-bold text-yellow-600">📌 置頂</span></label>
          <label class="flex items-center gap-2 cursor-pointer"><input v-model="editingPost.is_important" type="checkbox" class="w-4 h-4 text-red-600 rounded"><span class="text-sm font-bold text-red-600">🔥 重要</span></label>
        </div>

        <div>
          <label class="block text-xs text-gray-500 mb-1">說明</label>
          <textarea v-model="editingPost.description" class="border border-gray-300 p-2 w-full rounded text-sm rows-2"></textarea>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">主要網址</label>
          <input v-model="editingPost.url" type="url" class="border border-gray-300 p-2 w-full rounded text-sm">
        </div>

        <div class="bg-white p-3 rounded border border-gray-200">
          <div class="flex justify-between items-center mb-2">
            <label class="text-xs text-gray-500 font-bold">額外相關網址</label>
            <button @click="addLinkToObj(editingPost)" class="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded hover:bg-blue-200">+ 新增</button>
          </div>
          <div v-for="(link, index) in editingPost.links" :key="index" class="flex gap-2 mb-2 items-center">
            <input v-model="link.name" type="text" placeholder="名稱" class="border border-gray-300 p-1.5 text-sm rounded w-1/3">
            <input v-model="link.url" type="url" placeholder="https://..." class="border border-gray-300 p-1.5 text-sm rounded flex-1">
            <button @click="removeLinkFromObj(editingPost, index)" class="text-red-500 hover:text-red-700 font-bold px-2">✖</button>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-3">
          <button @click="cancelEdit" class="px-4 py-2 rounded text-sm text-gray-700 bg-gray-200 hover:bg-gray-300 transition-colors font-medium">取消</button>
          <button @click="saveEdit" :class="[themeObj.bg, themeObj.hover, 'text-white px-4 py-2 rounded text-sm transition-colors font-medium']">儲存變更</button>
        </div>
      </div>

      <ul class="space-y-3 max-h-[500px] overflow-y-auto pr-2">
        <li v-for="item in filteredSortedPosts" :key="item.id" class="flex flex-col md:flex-row justify-between md:items-center bg-white p-3 rounded-lg border shadow-sm hover:shadow-md transition-shadow" :class="item.is_important ? 'border-red-300 bg-red-50' : 'border-gray-200'">
          <div class="flex flex-col mb-2 md:mb-0">
            <div class="flex items-center gap-2 flex-wrap">
              <span v-if="item.is_pinned" class="bg-yellow-400 text-white text-[10px] px-1.5 py-0.5 rounded">📌</span>
              <span v-if="item.is_important" class="bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded">🔥</span>
              <span class="bg-gray-200 text-gray-700 text-xs font-bold px-2 py-0.5 rounded whitespace-nowrap">{{ item.category }}</span>
              <span class="font-bold text-gray-800 text-base" :class="{'text-red-700': item.is_important}">{{ item.title }}</span>
            </div>
            <div class="flex flex-col text-xs text-gray-500 mt-1 gap-1">
              <span>🕒 {{ formatDate(item.created_at) }}</span>
              <span class="truncate max-w-xs md:max-w-md">🔗 {{ item.url }}</span>
              <span v-if="item.links && item.links.length > 0" class="text-[10px] text-gray-400">+ 包含 {{ item.links.length }} 個額外網址</span>
            </div>
          </div>
          <div class="flex gap-2 self-end md:self-auto mt-2 md:mt-0">
            <button @click="startEdit(item)" :class="['text-sm px-3 py-1 rounded border transition-colors font-medium', themeObj.text, themeObj.bg.replace('bg-', 'border-'), themeObj.bg.replace('bg-', 'hover:bg-').replace('600', '50')]">編輯</button>
            <button @click="deletePost(item.id)" class="text-red-500 hover:bg-red-500 hover:text-white text-sm px-3 py-1 rounded border border-transparent hover:border-red-600 transition-colors font-medium">刪除</button>
          </div>
        </li>
        <li v-if="filteredSortedPosts.length === 0" class="text-center text-sm text-gray-400 py-8 border border-dashed border-gray-300 rounded-lg">這個分類目前沒有公告。</li>
      </ul>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { themeConfig } from '@/utils/theme'

const supabase = useSupabaseClient()
const dayjs = useDayjs()

const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const formatDate = (dateString) => dayjs(dateString).format('YYYY/MM/DD HH:mm')

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

// ====== 📝 一般 To-Do 暫存清單 ======
const todosList = ref([])
const newTodo = ref({ content: '', url: '', due_date: '' })

const loadTodos = async () => {
  const { data } = await supabase.from('todos').select('*').order('created_at', { ascending: false })
  if (data) todosList.value = data
}

const addTodo = async () => {
  if (!newTodo.value.content) return alert('內容不能為空！')
  const payload = { ...newTodo.value }
  if (!payload.due_date) payload.due_date = null
  await supabase.from('todos').insert([payload])
  newTodo.value = { content: '', url: '', due_date: '' }
  loadTodos()
}

const toggleTodo = async (todo) => {
  await supabase.from('todos').update({ is_completed: !todo.is_completed }).eq('id', todo.id)
  loadTodos()
}

const deleteTodo = async (id) => {
  if (!confirm('確定刪除這個項目嗎？')) return
  await supabase.from('todos').delete().eq('id', id)
  loadTodos()
}

const formatTodoDate = (dateString) => dayjs(dateString).format('MM/DD HH:mm')

// 一般 To-Do CSV 匯出匯入
const exportTodosCSV = () => {
  if (!todosList.value.length) return alert('沒有資料可以匯出！')
  const headers = ['內容(content)', '網址(url)', '期限(due_date)', '是否完成(is_completed)']
  let csvContent = headers.join(',') + '\n'
  todosList.value.forEach(t => {
    const content = `"${(t.content || '').replace(/"/g, '""')}"`
    const url = `"${(t.url || '').replace(/"/g, '""')}"`
    const dueDate = t.due_date ? `"${t.due_date}"` : '""'
    const isCompleted = t.is_completed ? 'TRUE' : 'FALSE'
    csvContent += [content, url, dueDate, isCompleted].join(',') + '\n'
  })
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `一般暫存清單_${dayjs().format('YYYYMMDD')}.csv`
  link.click()
}

const todoCsvInput = ref(null)
const handleTodoCsvImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async (e) => {
    const rows = parseCSVString(e.target.result)
    if (rows.length < 2) return alert('CSV 格式錯誤！')
    const insertData = []
    for (let i = 1; i < rows.length; i++) {
      if (rows[i].length < 4) continue
      let dDate = rows[i][2].replace(/"/g, '').trim()
      insertData.push({
        content: rows[i][0],
        url: rows[i][1],
        due_date: dDate ? dDate : null,
        is_completed: rows[i][3].trim().toUpperCase() === 'TRUE'
      })
    }
    if (insertData.length > 0) {
      await supabase.from('todos').insert(insertData)
      alert(`成功匯入 ${insertData.length} 筆紀錄！`)
      loadTodos()
    }
    todoCsvInput.value.value = ''
  }
  reader.readAsText(file)
}

// ====== 📢 前台教學內容 ======
const categories = ref([])
const posts = ref([])
const activePublicTab = ref('todos')
const postSort = ref('newest')
const getEmptyPost = () => ({ title: '', description: '', url: '', category: '', is_important: false, is_pinned: false, links: [] })
const newPost = ref(getEmptyPost()) 
const editingPost = ref(null)

const loadCats = async () => { 
  const { data } = await supabase.from('post_categories').select('*').order('id', { ascending: true })
  if(data) { 
    categories.value = data
    if(data.length && !newPost.value.category) newPost.value.category = data[0].name 
  } 
}

const loadPosts = async () => { 
  const { data } = await supabase.from('bulletins').select('*').order('is_pinned', { ascending: false }).order('created_at', { ascending: false })
  if(data) posts.value = data 
}

const selectCategoryTab = (category) => {
  activePublicTab.value = category
  newPost.value.category = category
}

const filteredSortedPosts = computed(() => {
  const filtered = posts.value.filter(post => post.category === activePublicTab.value)
  return [...filtered].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime()
    const dateB = new Date(b.created_at).getTime()
    if (postSort.value === 'oldest') return dateA - dateB
    if (postSort.value === 'important') {
      if (Boolean(a.is_important) !== Boolean(b.is_important)) return a.is_important ? -1 : 1
      if (Boolean(a.is_pinned) !== Boolean(b.is_pinned)) return a.is_pinned ? -1 : 1
    }
    return dateB - dateA
  })
})

const addPost = async () => {
  if (!newPost.value.title || !newPost.value.url) return alert('標題與網址必填！')
  if (!newPost.value.category) return alert('請選擇前台分類！')
  const publishedCategory = newPost.value.category
  await supabase.from('bulletins').insert([{ ...newPost.value }])
  alert('發布成功！')
  activePublicTab.value = publishedCategory
  newPost.value = getEmptyPost()
  newPost.value.category = publishedCategory
  loadPosts() 
}

const deletePost = async (id) => { 
  if (confirm('確定刪除？')) { 
    await supabase.from('bulletins').delete().eq('id', id)
    loadPosts() 
  } 
}

const startEdit = (post) => { editingPost.value = JSON.parse(JSON.stringify({ ...post, links: post.links || [] })) }
const cancelEdit = () => { editingPost.value = null }
const saveEdit = async () => {
  if (!editingPost.value.title || !editingPost.value.url) return alert('標題與網址必填！')
  const { id, title, description, url, category, is_important, is_pinned, links } = editingPost.value
  await supabase.from('bulletins').update({ title, description, url, category, is_important, is_pinned, links }).eq('id', id)
  alert('更新成功！')
  activePublicTab.value = category
  editingPost.value = null 
  loadPosts() 
}

const addLinkToObj = (obj) => {
  if (!obj.links) obj.links = []
  obj.links.push({ name: '', url: '' })
}
const removeLinkFromObj = (obj, index) => { obj.links.splice(index, 1) }

// 生命週期載入
onMounted(() => { 
  loadTodos()
  loadCats()
  loadPosts() 
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
