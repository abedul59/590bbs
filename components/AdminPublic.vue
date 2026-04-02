<template>
  <div class="space-y-8">
    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 class="text-xl font-semibold mb-4">📝 一般管理暫存清單</h3>
      <div class="flex gap-2 mb-4 bg-gray-50 p-3 rounded-lg">
        <input v-model="newTodo.content" placeholder="備忘錄..." class="border p-2 flex-1 rounded text-sm">
        <button @click="addTodo" class="bg-gray-800 text-white px-4 py-2 rounded">新增</button>
      </div>
      <ul class="space-y-2 max-h-[300px] overflow-y-auto pr-2">
        <li v-for="t in todosList" :key="t.id" class="flex justify-between items-center p-3 rounded border bg-white">
          <span>{{ t.content }}</span>
          <button @click="deleteTodo(t.id)" class="text-red-500">✖</button>
        </li>
      </ul>
    </section>

    <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 class="text-xl font-semibold mb-4">📢 編輯前台教學內容</h3>
      <div class="bg-gray-50 p-4 rounded-xl border mb-6">
        <div class="flex gap-3 mb-3">
          <select v-model="newPost.category" class="border p-2 rounded w-1/3">
            <option v-for="c in categories" :key="c.id" :value="c.name">{{ c.name }}</option>
          </select>
          <input v-model="newPost.title" placeholder="教學標題" class="border p-2 flex-1 rounded">
        </div>
        <input v-model="newPost.url" placeholder="網址" class="border p-2 w-full mb-3 rounded">
        <button @click="addPost" class="bg-blue-600 text-white px-6 py-2 rounded">發布</button>
      </div>
      
      <ul class="space-y-3">
        <li v-for="p in posts" :key="p.id" class="bg-white p-3 rounded border flex justify-between items-center">
          <div>
            <span class="bg-gray-200 text-xs px-2 py-1 rounded mr-2">{{ p.category }}</span>
            <span class="font-bold">{{ p.title }}</span>
          </div>
          <button @click="deletePost(p.id)" class="text-red-500">刪除</button>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const supabase = useSupabaseClient()

const todosList = ref([]); const newTodo = ref({ content: '' })
const categories = ref([]); const posts = ref([]); const newPost = ref({ category: '', title: '', url: '' })

onMounted(() => { loadTodos(); loadCats(); loadPosts() })

const loadTodos = async () => { const { data } = await supabase.from('todos').select('*'); if(data) todosList.value=data }
const addTodo = async () => { await supabase.from('todos').insert([newTodo.value]); newTodo.value.content=''; loadTodos() }
const deleteTodo = async (id) => { await supabase.from('todos').delete().eq('id',id); loadTodos() }

const loadCats = async () => { const { data } = await supabase.from('post_categories').select('*'); if(data) { categories.value=data; if(data.length) newPost.value.category=data[0].name } }
const loadPosts = async () => { const { data } = await supabase.from('bulletins').select('*').order('created_at',{ascending:false}); if(data) posts.value=data }
const addPost = async () => { await supabase.from('bulletins').insert([newPost.value]); newPost.value.title=''; newPost.value.url=''; loadPosts() }
const deletePost = async (id) => { await supabase.from('bulletins').delete().eq('id',id); loadPosts() }
</script>