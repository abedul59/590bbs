<template>
  <div class="min-h-screen bg-gray-50 font-sans">
    <div class="bg-blue-600 text-white overflow-hidden whitespace-nowrap py-2 px-4 relative">
      <div class="inline-block animate-marquee">
        📢 {{ settings?.marquee_text || '歡迎來到教學佈告欄...' }}
      </div>
    </div>

    <header class="bg-white shadow-sm p-4 flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-800">{{ settings?.title || '教學佈告欄' }}</h1>
      <NuxtLink to="/admin" class="text-sm text-gray-500 hover:text-blue-600">管理後台</NuxtLink>
    </header>

    <main class="container mx-auto p-4 max-w-4xl">
      <NuxtPage />
    </main>
  </div>
</template>

<script setup>
const supabase = useSupabaseClient()
const { data: settings } = await useAsyncData('settings', async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  return data
})
</script>

<style>
/* 跑馬燈動畫 */
@keyframes marquee {
  0% { transform: translateX(100vw); }
  100% { transform: translateX(-100%); }
}
.animate-marquee {
  animation: marquee 15s linear infinite;
}
</style>