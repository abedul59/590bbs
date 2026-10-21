<template>
  <div class="fixed inset-0 z-[90] flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal="true" aria-labelledby="quick-create-title" @click.self="emit('close')">
    <div class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-white p-5 shadow-2xl md:p-6">
      <div class="mb-4 flex items-center justify-between border-b border-gray-200 pb-3">
        <h2 id="quick-create-title" class="text-xl font-bold text-gray-900">新增公告</h2>
        <button type="button" class="rounded-lg px-3 py-1.5 font-bold text-gray-500 hover:bg-gray-100 hover:text-gray-800" aria-label="關閉" @click="emit('close')">✕</button>
      </div>

      <div class="mb-5 grid grid-cols-2 gap-2 rounded-xl bg-gray-100 p-1.5">
        <button type="button" class="rounded-lg px-4 py-2.5 text-sm font-bold transition" :class="activeTab === 'bulletin' ? [themeObj.bg, 'text-white shadow-sm'] : 'text-gray-600 hover:bg-white'" @click="activeTab = 'bulletin'">
          📢 新增前台公告
        </button>
        <button type="button" class="rounded-lg px-4 py-2.5 text-sm font-bold transition" :class="activeTab === 'todo' ? [themeObj.bg, 'text-white shadow-sm'] : 'text-gray-600 hover:bg-white'" @click="activeTab = 'todo'">
          📝 新增暫存
        </button>
      </div>

      <p v-if="errorMessage" class="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-bold text-red-700">{{ errorMessage }}</p>
      <p v-if="successMessage" class="mb-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm font-bold text-green-700">{{ successMessage }}</p>

      <form v-if="activeTab === 'bulletin'" class="space-y-4" @submit.prevent="addBulletin">
        <div class="grid gap-3 md:grid-cols-[1fr_2fr]">
          <label class="text-sm font-bold text-gray-700">
            分類
            <select v-model="newPost.category" required class="mt-1 w-full rounded-lg border border-gray-300 bg-white p-2.5 font-normal outline-none focus:ring-2" :class="themeObj.ring">
              <option value="" disabled>選擇分類</option>
              <option v-for="category in categories" :key="category.id" :value="category.name">{{ category.icon }} {{ category.name }}</option>
            </select>
          </label>
          <label class="text-sm font-bold text-gray-700">
            標題
            <input v-model.trim="newPost.title" type="text" required class="mt-1 w-full rounded-lg border border-gray-300 p-2.5 font-normal outline-none focus:ring-2" :class="themeObj.ring" placeholder="輸入公告標題">
          </label>
        </div>

        <div class="flex flex-wrap gap-5">
          <label class="flex cursor-pointer items-center gap-2 text-sm font-bold text-yellow-700"><input v-model="newPost.is_pinned" type="checkbox" class="h-4 w-4">📌 置頂公告</label>
          <label class="flex cursor-pointer items-center gap-2 text-sm font-bold text-red-600"><input v-model="newPost.is_important" type="checkbox" class="h-4 w-4">🔥 標記重要</label>
        </div>

        <label class="block text-sm font-bold text-gray-700">
          說明
          <textarea v-model="newPost.description" rows="4" class="mt-1 w-full rounded-lg border border-gray-300 p-2.5 font-normal outline-none focus:ring-2" :class="themeObj.ring" placeholder="輸入公告內容" />
        </label>

        <label class="block text-sm font-bold text-gray-700">
          主要網址
          <input v-model.trim="newPost.url" type="url" required class="mt-1 w-full rounded-lg border border-gray-300 p-2.5 font-normal outline-none focus:ring-2" :class="themeObj.ring" placeholder="https://...">
        </label>

        <div class="rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div class="mb-2 flex items-center justify-between">
            <span class="text-sm font-bold text-gray-700">額外相關網址</span>
            <button type="button" class="rounded bg-blue-100 px-2 py-1 text-xs font-bold text-blue-700 hover:bg-blue-200" @click="newPost.links.push({ name: '', url: '' })">＋ 新增網址</button>
          </div>
          <div v-for="(link, index) in newPost.links" :key="index" class="mb-2 flex gap-2 last:mb-0">
            <input v-model.trim="link.name" type="text" class="w-1/3 rounded border border-gray-300 p-2 text-sm" placeholder="名稱">
            <input v-model.trim="link.url" type="url" class="min-w-0 flex-1 rounded border border-gray-300 p-2 text-sm" placeholder="https://...">
            <button type="button" class="px-2 font-bold text-red-500" aria-label="移除網址" @click="newPost.links.splice(index, 1)">✕</button>
          </div>
        </div>

        <div class="flex justify-end gap-2 border-t pt-4">
          <button type="button" class="rounded-lg bg-gray-100 px-4 py-2.5 font-bold text-gray-700 hover:bg-gray-200" @click="emit('close')">完成</button>
          <button type="submit" :disabled="saving" :class="[themeObj.bg, themeObj.hover, 'rounded-lg px-5 py-2.5 font-bold text-white disabled:opacity-50']">{{ saving ? '發布中…' : '發布公告' }}</button>
        </div>
      </form>

      <form v-else class="space-y-4" @submit.prevent="addTodo">
        <label class="block text-sm font-bold text-gray-700">
          暫存內容
          <textarea v-model="newTodo.content" rows="4" required class="mt-1 w-full rounded-lg border border-gray-300 p-2.5 font-normal outline-none focus:ring-2" :class="themeObj.ring" placeholder="輸入備忘、草稿或代辦事項" />
        </label>
        <label class="block text-sm font-bold text-gray-700">
          附加網址（選填）
          <input v-model.trim="newTodo.url" type="url" class="mt-1 w-full rounded-lg border border-gray-300 p-2.5 font-normal outline-none focus:ring-2" :class="themeObj.ring" placeholder="https://...">
        </label>
        <label class="block text-sm font-bold text-gray-700">
          指定日期時間（選填）
          <input v-model="newTodo.due_date" type="datetime-local" class="mt-1 w-full rounded-lg border border-gray-300 p-2.5 font-normal outline-none focus:ring-2" :class="themeObj.ring">
        </label>
        <div class="flex justify-end gap-2 border-t pt-4">
          <button type="button" class="rounded-lg bg-gray-100 px-4 py-2.5 font-bold text-gray-700 hover:bg-gray-200" @click="emit('close')">完成</button>
          <button type="submit" :disabled="saving" :class="[themeObj.bg, themeObj.hover, 'rounded-lg px-5 py-2.5 font-bold text-white disabled:opacity-50']">{{ saving ? '儲存中…' : '加入暫存' }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { themeConfig } from '@/utils/theme'

const props = defineProps({
  categories: { type: Array, default: () => [] }
})
const emit = defineEmits(['close', 'post-created'])

const supabase = useSupabaseClient()
const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)
const activeTab = ref('bulletin')
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const emptyPost = () => ({ title: '', description: '', url: '', category: props.categories[0]?.name || '', is_important: false, is_pinned: false, links: [] })
const newPost = reactive(emptyPost())
const newTodo = reactive({ content: '', url: '', due_date: '' })

watch(() => props.categories, (categories) => {
  if (!newPost.category && categories.length) newPost.category = categories[0].name
}, { immediate: true })

const resetMessages = () => {
  errorMessage.value = ''
  successMessage.value = ''
}

const addBulletin = async () => {
  resetMessages()
  if (!newPost.category || !newPost.title || !newPost.url) {
    errorMessage.value = '分類、標題與主要網址為必填。'
    return
  }
  saving.value = true
  const payload = {
    ...newPost,
    links: newPost.links.filter(link => link.name || link.url)
  }
  const { data, error } = await supabase.from('bulletins').insert([payload]).select().single()
  saving.value = false
  if (error) {
    errorMessage.value = `發布失敗：${error.message}`
    return
  }
  emit('post-created', data)
  const category = newPost.category
  Object.assign(newPost, emptyPost(), { category })
  successMessage.value = '公告已發布並顯示於首頁。'
}

const addTodo = async () => {
  resetMessages()
  if (!newTodo.content.trim()) {
    errorMessage.value = '暫存內容不能為空。'
    return
  }
  saving.value = true
  const { error } = await supabase.from('todos').insert([{
    content: newTodo.content.trim(),
    url: newTodo.url || '',
    due_date: newTodo.due_date || null
  }])
  saving.value = false
  if (error) {
    errorMessage.value = `儲存失敗：${error.message}`
    return
  }
  Object.assign(newTodo, { content: '', url: '', due_date: '' })
  successMessage.value = '內容已加入後台暫存清單。'
}
</script>
