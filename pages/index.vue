<template>
  <div>
    <div class="flex justify-center space-x-2 md:space-x-4 mt-6 mb-6 flex-wrap gap-y-3">
      <button 
        v-for="cat in categories" :key="cat.id"
        @click="activeCategory = cat.name"
        :class="activeCategory === cat.name ? [themeObj.bg, 'text-white shadow-md'] : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'"
        class="px-5 py-2.5 md:px-6 md:py-3 rounded-full font-bold text-sm md:text-base transition-all duration-300 flex items-center gap-2"
      >
        <span>{{ cat.icon }}</span> {{ cat.name }}
      </button>
      <div v-if="categories.length === 0" class="text-sm text-gray-400">目前尚無分類，請至後台新增。</div>
    </div>

    <div class="mb-8 max-w-2xl mx-auto bg-blue-50 border border-blue-200 p-4 md:p-6 rounded-2xl shadow-sm text-center flex flex-col items-center justify-center animate-fade-in relative overflow-hidden">
      <div class="absolute top-0 right-0 -mt-4 -mr-4 text-blue-200 opacity-30 text-8xl pointer-events-none">✨</div>
      
      <h4 class="font-bold text-blue-900 mb-2 text-lg relative z-10">📅 每日學習打卡</h4>
      <p class="text-sm text-blue-600 mb-4 relative z-10">
        記錄你的每一天，保持學習好習慣！
      </p>
      
      <button 
        @click="manualCheckIn" 
        :disabled="hasCheckedIn"
        class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-10 rounded-full shadow-md transition-all transform hover:scale-105 disabled:opacity-80 disabled:hover:scale-100 disabled:cursor-not-allowed flex items-center gap-2 relative z-10"
      >
        <span>{{ hasCheckedIn ? '🎉 你今日已成功簽到' : '✋ 點我進行學生簽到' }}</span>
      </button>
    </div>

    <div v-if="filteredBulletins.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
      <div 
        v-for="item in filteredBulletins" 
        :key="item.id" 
        :class="[
          'relative p-6 rounded-xl shadow-sm hover:shadow-md transition duration-300 group flex flex-col h-full',
          item.is_important ? `bg-red-50 border-2 border-red-400` : 'bg-white border border-gray-200'
        ]"
      >
        <div class="absolute -top-3 -right-2 flex gap-1">
          <span v-if="item.is_pinned" class="bg-yellow-400 text-white text-xs font-bold px-2 py-1 rounded-full shadow">📌 置頂</span>
          <span v-if="item.is_important" class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow">🔥 重要</span>
        </div>

        <div v-if="editingPost?.id === item.id" class="flex-1 space-y-3">
          <div class="flex flex-col sm:flex-row gap-3">
            <select v-model="editingPost.category" class="border border-gray-300 p-2 rounded bg-white sm:w-1/3">
              <option v-for="cat in categories" :key="cat.id" :value="cat.name">{{ cat.icon }} {{ cat.name }}</option>
            </select>
            <input v-model="editingPost.title" type="text" class="border border-gray-300 p-2 rounded flex-1" aria-label="文章標題">
          </div>
          <textarea v-model="editingPost.description" rows="3" class="border border-gray-300 p-2 rounded w-full" aria-label="文章內容"></textarea>
          <input v-model="editingPost.url" type="url" class="border border-gray-300 p-2 rounded w-full" aria-label="主要網址">
          <div class="flex flex-wrap gap-4">
            <label class="flex items-center gap-2 text-sm font-bold text-yellow-700"><input v-model="editingPost.is_pinned" type="checkbox">📌 置頂</label>
            <label class="flex items-center gap-2 text-sm font-bold text-red-600"><input v-model="editingPost.is_important" type="checkbox">🔥 重要</label>
          </div>
          <div class="bg-white/70 border border-gray-200 rounded-lg p-3">
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-bold text-gray-600">額外相關網址</span>
              <button type="button" @click="editingPost.links.push({ name: '', url: '' })" class="text-xs text-blue-600 hover:underline">＋新增網址</button>
            </div>
            <div v-for="(link, linkIndex) in editingPost.links" :key="linkIndex" class="flex gap-2 mb-2">
              <input v-model="link.name" type="text" placeholder="名稱" class="border border-gray-300 p-1.5 rounded w-1/3 text-sm">
              <input v-model="link.url" type="url" placeholder="https://..." class="border border-gray-300 p-1.5 rounded flex-1 text-sm">
              <button type="button" @click="editingPost.links.splice(linkIndex, 1)" class="text-red-500 px-2" aria-label="移除網址">✖</button>
            </div>
          </div>
          <div class="flex justify-end gap-2">
            <button type="button" @click="editingPost = null" class="px-4 py-2 rounded-lg bg-gray-200 text-gray-700 text-sm font-bold">取消</button>
            <button type="button" @click="savePost" :disabled="savingPost" :class="[themeObj.bg, themeObj.hover, 'px-4 py-2 rounded-lg text-white text-sm font-bold disabled:opacity-60']">{{ savingPost ? '儲存中…' : '儲存變更' }}</button>
          </div>
        </div>

        <div v-else class="flex-1">
          <div class="text-xs text-gray-400 mb-2 flex items-center gap-1 font-mono">
            🕒 {{ formatDate(item.created_at) }}
          </div>
          
          <h5 :class="['text-xl font-bold tracking-tight transition-colors duration-300 mb-2 pr-10', item.is_important ? 'text-red-700' : 'text-gray-900', themeObj.hoverText]">
            {{ item.title }}
          </h5>
          <p class="font-normal text-gray-600 whitespace-pre-line">{{ item.description }}</p>
        </div>

        <div v-if="editingPost?.id !== item.id" class="mt-5 flex flex-wrap gap-2">
          <a :href="item.url" target="_blank" :class="[themeObj.bg, themeObj.hover, 'text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm transition-colors']">
            前往主連結 🚀
          </a>
          <a 
            v-for="(link, index) in item.links || []" 
            :key="index"
            :href="link.url" 
            target="_blank"
            class="bg-white border border-gray-300 text-gray-700 hover:bg-gray-100 px-4 py-2 rounded-lg text-sm font-bold shadow-sm transition-colors"
          >
            {{ link.name || '參考網址' }}
          </a>
          <div class="ml-auto flex gap-2">
            <button type="button" @click="beginEdit(item)" class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-2 rounded-lg text-sm font-bold transition-colors">編輯</button>
            <button type="button" @click="removePost(item)" class="bg-red-50 hover:bg-red-100 text-red-600 px-3 py-2 rounded-lg text-sm font-bold transition-colors">刪除</button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-16 text-gray-400 animate-fade-in">
      <div class="text-4xl mb-3">📭</div>
      <p>目前這個科目還沒有教學內容喔！</p>
    </div>

    <Teleport to="body">
      <div
        v-if="teacherPasswordDialogOpen"
        class="fixed inset-0 z-[100] bg-black/50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="teacher-password-title"
        @click.self="cancelTeacherAuthorization"
      >
        <form class="bg-white w-full max-w-sm rounded-2xl shadow-2xl p-6" @submit.prevent="submitTeacherPassword">
          <h3 id="teacher-password-title" class="text-lg font-bold text-gray-900 mb-4">導師驗證</h3>
          <label for="teacher-password" class="block text-sm font-medium text-gray-700 mb-2">請輸入導師動態密碼</label>
          <input
            id="teacher-password"
            ref="teacherPasswordField"
            v-model="teacherPassword"
            type="password"
            autocomplete="current-password"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
          <p v-if="teacherPasswordError" class="text-sm text-red-600 mt-2" role="alert">{{ teacherPasswordError }}</p>
          <div class="flex justify-end gap-2 mt-5">
            <button type="button" class="px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold" @click="cancelTeacherAuthorization">取消</button>
            <button type="submit" :class="[themeObj.bg, themeObj.hover, 'px-4 py-2 rounded-lg text-white font-bold']">確認</button>
          </div>
        </form>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { themeConfig } from '@/utils/theme'
import { getTodayPassword } from '@/utils/auth'

const supabase = useSupabaseClient()
const dayjs = useDayjs()
const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const activeCategory = ref('')
const teacherAuthorized = ref(false)
const editingPost = ref(null)
const savingPost = ref(false)
const teacherPasswordDialogOpen = ref(false)
const teacherPassword = ref('')
const teacherPasswordError = ref('')
const teacherPasswordField = ref(null)
let pendingTeacherAction = null

const requestTeacherAuthorization = async (action) => {
  if (teacherAuthorized.value) {
    await action()
    return
  }

  pendingTeacherAction = action
  teacherPassword.value = ''
  teacherPasswordError.value = ''
  teacherPasswordDialogOpen.value = true
  await nextTick()
  teacherPasswordField.value?.focus()
}

const cancelTeacherAuthorization = () => {
  teacherPasswordDialogOpen.value = false
  teacherPassword.value = ''
  teacherPasswordError.value = ''
  pendingTeacherAction = null
}

const submitTeacherPassword = async () => {
  if (teacherPassword.value !== getTodayPassword()) {
    teacherPassword.value = ''
    teacherPasswordError.value = '密碼錯誤'
    await nextTick()
    teacherPasswordField.value?.focus()
    return
  }

  teacherAuthorized.value = true
  teacherPasswordDialogOpen.value = false
  teacherPassword.value = ''
  teacherPasswordError.value = ''
  const action = pendingTeacherAction
  pendingTeacherAction = null
  await action?.()
}

const beginEdit = (post) => {
  requestTeacherAuthorization(() => {
    editingPost.value = JSON.parse(JSON.stringify({ ...post, links: post.links || [] }))
  })
}

const savePost = async () => {
  if (!editingPost.value?.title || !editingPost.value?.url || !editingPost.value?.category) {
    window.alert('分類、標題與主要網址為必填')
    return
  }
  savingPost.value = true
  const { id, title, description, url, category, is_important, is_pinned, links } = editingPost.value
  const payload = { title, description, url, category, is_important, is_pinned, links }
  const { error } = await supabase.from('bulletins').update(payload).eq('id', id)
  savingPost.value = false
  if (error) {
    window.alert(`儲存失敗：${error.message}`)
    return
  }
  bulletins.value = (bulletins.value || []).map(post => post.id === id ? { ...post, ...payload } : post)
  editingPost.value = null
  window.alert('文章已更新')
}

const removePost = async (post) => {
  await requestTeacherAuthorization(async () => {
    if (!window.confirm(`確定刪除「${post.title}」嗎？`)) return
    const { error } = await supabase.from('bulletins').delete().eq('id', post.id)
    if (error) {
      window.alert(`刪除失敗：${error.message}`)
      return
    }
    bulletins.value = (bulletins.value || []).filter(item => item.id !== post.id)
    if (editingPost.value?.id === post.id) editingPost.value = null
  })
}

// ====== 🌟 極速背景打卡與保活邏輯 ======
const hasCheckedIn = ref(false)

const performSystemBackgroundTasks = (actionType = 'auto_login') => {
  if (hasCheckedIn.value) return
  
  // 1. UI 瞬間反應：不讓學生等待，直接將按鈕設為已打卡
  hasCheckedIn.value = true

  // 2. 把繁重的網路請求丟進背景執行 (Fire and forget)，不阻塞畫面
  setTimeout(async () => {
    try {
      // 寫入 Supabase (學生打卡紀錄)
      await supabase.from('system_keepalive_logs').insert([
        { action_type: actionType }
      ])

      // 動態去資料庫抓取 Vercel 與 Render 網址
      const { data: keepAliveUrls } = await supabase.from('keep_alive_urls').select('url')

      // 背景並發戳醒它們，不等待結果
      if (keepAliveUrls && keepAliveUrls.length > 0) {
        keepAliveUrls.forEach(item => {
          if (!item.url) return
          const separator = item.url.includes('?') ? '&' : '?'
          fetch(`${item.url}${separator}_ping=${Date.now()}`, { 
            method: 'GET', 
            mode: 'no-cors',
            cache: 'no-store'
          }).catch(() => {}) 
        })
      }
    } catch (error) {
      console.error('背景打卡作業失敗', error)
    }
  }, 0)
}

// 網頁載入後，自動延遲 1 秒執行背景打卡
onMounted(() => {
  setTimeout(() => {
    performSystemBackgroundTasks('auto_visitor_wakeup')
  }, 1000)
})

// 學生手動點擊打卡
const manualCheckIn = () => {
  if (hasCheckedIn.value) {
    alert('🎉 你今日已經完成簽到囉！繼續保持！')
    return
  }
  performSystemBackgroundTasks('manual_student_checkin')
  alert('🎉 簽到成功！你今日成功打卡了！')
}
// ==========================================

// 取得前台動態分類
const { data: categories } = await useAsyncData('categories', async () => {
  const { data } = await supabase.from('post_categories').select('*').order('id', { ascending: true })
  return data || []
})

if (categories.value && categories.value.length > 0) {
  activeCategory.value = categories.value[0].name
}

const { data: settings } = await useAsyncData('site_settings', async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  return data
})
const sortOrder = computed(() => settings.value?.sort_order || 'newest')

const { data: bulletins } = await useAsyncData('bulletins', async () => {
  const { data } = await supabase.from('bulletins').select('*')
  return data
})

const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY/MM/DD HH:mm')
}

const filteredBulletins = computed(() => {
  if (!bulletins.value) return []
  let filtered = bulletins.value.filter(b => b.category === activeCategory.value)
  
  return filtered.sort((a, b) => {
    if (a.is_pinned !== b.is_pinned) {
      return a.is_pinned ? -1 : 1 
    }
    const dateA = new Date(a.created_at).getTime()
    const dateB = new Date(b.created_at).getTime()
    
    if (sortOrder.value === 'oldest') {
      return dateA - dateB
    } else {
      return dateB - dateA
    }
  })
})
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
