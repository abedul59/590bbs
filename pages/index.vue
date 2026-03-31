<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
    <a 
      v-for="item in bulletins" 
      :key="item.id" 
      :href="item.url" 
      target="_blank"
      class="block p-6 bg-white rounded-lg border border-gray-200 shadow-md hover:bg-gray-100 transition duration-200"
    >
      <h5 class="mb-2 text-xl font-bold tracking-tight text-gray-900">{{ item.title }}</h5>
      <p class="font-normal text-gray-700">{{ item.description }}</p>
      <div class="mt-4 text-sm text-blue-500 flex items-center">
        點擊前往學習 ➡️
      </div>
    </a>
  </div>
</template>

<script setup>
const supabase = useSupabaseClient()
// 取得佈告欄資料，依時間反序排列
const { data: bulletins } = await useAsyncData('bulletins', async () => {
  const { data } = await supabase.from('bulletins').select('*').order('created_at', { ascending: false })
  return data
})
</script>