<template>
  <div class="mt-10 bg-white p-6 md:p-10 rounded-xl shadow-lg transition-colors duration-300 relative overflow-hidden">
    
    <div v-if="showRenderToast" class="fixed bottom-10 right-10 bg-green-600 text-white px-6 py-4 rounded-xl shadow-2xl z-50 animate-bounce-in flex items-center gap-4 border-2 border-white">
      <span class="text-3xl animate-pulse">🛸</span>
      <div>
        <h4 class="font-bold text-lg">Render 喚醒就緒！</h4>
        <p class="text-sm opacity-90">已過 60 秒，伺服器應該已完成冷啟動。</p>
      </div>
      <button @click="showRenderToast = false" class="ml-4 hover:text-gray-200 font-bold text-xl">✖</button>
    </div>

    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">後台管理</h2>
      <button v-if="isAuthenticated" @click="logout" class="text-gray-500 hover:text-red-600 text-sm font-bold flex items-center gap-1 transition-colors">
        🚪 登出
      </button>
    </div>

    <div v-if="!isAuthenticated" class="space-y-4">
      <label class="block text-sm font-medium text-gray-700">請輸入今日動態密碼</label>
      <input v-model="inputPassword" type="password" class="border border-gray-300 rounded p-2 w-full focus:outline-none focus:ring-2 focus:border-transparent" :class="themeObj.ring" @keyup.enter="login">
      <p v-if="errorMsg" class="text-red-500 text-sm">{{ errorMsg }}</p>
      <button @click="login" :class="[themeObj.bg, themeObj.hover, 'text-white px-4 py-2 rounded w-full transition duration-300']">登入</button>
    </div>

    <div v-else class="space-y-8 animate-fade-in">
      
      <section class="border-b pb-6">
        <h3 class="text-xl font-semibold mb-4">網站全域設定</h3>
        <div class="space-y-3">
          <div class="flex flex-col md:flex-row gap-3">
            <div class="flex-1">
              <label class="block text-sm text-gray-600 mb-1">網站名稱</label>
              <input v-model="siteTitle" type="text" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
            </div>
            <div class="md:w-1/4">
              <label class="block text-sm text-gray-600 mb-1">網站風格主題</label>
              <select v-model="siteTheme" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent bg-white', themeObj.ring]">
                <option v-for="(config, key) in themeConfig" :key="key" :value="key">{{ config.label }}</option>
              </select>
            </div>
            <div class="md:w-1/4">
              <label class="block text-sm text-gray-600 mb-1">前台公告排序方式</label>
              <select v-model="siteSortOrder" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent bg-white', themeObj.ring]">
                <option value="newest">🕒 最新公告在前</option>
                <option value="oldest">🕰️ 最舊公告在前</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">跑馬燈內容</label>
            <input v-model="marqueeText" type="text" :class="['border border-gray-300 p-2 w-full rounded focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
          </div>
          <button @click="updateSettings" :class="[themeObj.bg, themeObj.hover, 'text-white px-6 py-2 rounded font-medium transition duration-300 shadow-sm']">儲存全域設定</button>
        </div>
      </section>

      <section class="border-b pb-6">
        <h3 class="text-xl font-semibold mb-4 flex items-center gap-2">
          🔒 後台專屬私密分頁 
          <span class="text-xs bg-gray-800 text-white px-2 py-1 rounded shadow-sm">僅限管理員可見</span>
        </h3>

        <div class="flex flex-wrap items-center gap-2 mb-6 bg-gray-50 p-2 rounded-lg border border-gray-200">
          <button 
            v-for="tab in adminTabs" :key="tab.id"
            @click="activeAdminTab = tab.id"
            :class="[activeAdminTab === tab.id ? themeObj.bg + ' text-white shadow-md' : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100', 'px-4 py-2 rounded-full font-bold text-sm transition-all flex items-center gap-2 group']"
          >
            {{ tab.name }}
            <span @click.stop="deleteAdminTab(tab.id)" class="text-xs opacity-50 group-hover:opacity-100 hover:text-red-500 transition-opacity">✖</span>
          </button>
          
          <div class="flex items-center ml-auto bg-white border border-gray-300 rounded-full overflow-hidden shadow-sm">
            <input v-model="newAdminTabName" type="text" placeholder="+ 新增分頁" class="text-sm px-3 py-2 w-32 focus:outline-none" @keyup.enter="addAdminTab">
            <button @click="addAdminTab" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-2 text-sm font-bold transition-colors border-l border-gray-300">新增</button>
          </div>
        </div>

        <div v-if="activeAdminTab" class="bg-blue-50 border border-blue-100 p-4 rounded-xl animate-fade-in relative">
          <h4 class="font-bold text-blue-800 mb-3 flex justify-between items-center border-b border-blue-200 pb-2">
            <span>📝 在「{{ currentTabName }}」新增私密內容</span>
          </h4>

          <div v-if="editingAdminNote" class="bg-white p-4 rounded-lg shadow-sm border border-yellow-300 mb-4 ring-2 ring-yellow-200">
            <h5 class="text-xs font-bold text-yellow-600 mb-2">✏️ 編輯模式中</h5>
            <input v-model="editingAdminNote.title" type="text" placeholder="標題 (必填)" class="border border-gray-300 p-2 w-full rounded text-sm mb-2">
            <textarea v-model="editingAdminNote.description" placeholder="內容說明..." class="border border-gray-300 p-2 w-full rounded text-sm mb-2 rows-2"></textarea>
            <input v-model="editingAdminNote.url" type="url" placeholder="主要網址 (選填)" class="border border-gray-300 p-2 w-full rounded text-sm mb-2">
            
            <div class="flex gap-4 mb-2">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="editingAdminNote.is_pinned" type="checkbox" class="w-4 h-4 rounded">
                <span class="text-xs font-bold text-yellow-600">📌 置頂</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="editingAdminNote.is_important" type="checkbox" class="w-4 h-4 rounded">
                <span class="text-xs font-bold text-red-600">🔥 重要</span>
              </label>
            </div>
            
            <div class="bg-gray-50 p-2 rounded mb-2 border border-gray-200">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs text-gray-500 font-bold">額外網址</span>
                <button @click="addLinkToObj(editingAdminNote)" class="text-[10px] bg-gray-200 px-2 py-0.5 rounded">+ 新增</button>
              </div>
              <div v-for="(link, index) in editingAdminNote.links" :key="index" class="flex gap-1 mb-1 items-center">
                <input v-model="link.name" type="text" placeholder="名稱" class="border border-gray-300 p-1 text-xs rounded w-1/3">
                <input v-model="link.url" type="url" placeholder="網址" class="border border-gray-300 p-1 text-xs rounded flex-1">
                <button @click="removeLinkFromObj(editingAdminNote, index)" class="text-red-500 text-xs px-1">✖</button>
              </div>
            </div>
            
            <div class="flex justify-end gap-2">
              <button @click="cancelEditAdminNote" class="text-xs px-3 py-1.5 bg-gray-200 rounded hover:bg-gray-300 font-bold">取消</button>
              <button @click="saveAdminNote" class="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 font-bold">儲存變更</button>
            </div>
          </div>

          <div v-else class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
            <div class="flex gap-2 mb-2">
              <input v-model="newAdminNote.title" type="text" placeholder="標題 (必填)" class="border border-gray-300 p-2 w-full rounded text-sm focus:ring-1 focus:ring-blue-300">
            </div>
            <textarea v-model="newAdminNote.description" placeholder="內容說明..." class="border border-gray-300 p-2 w-full rounded text-sm mb-2 focus:ring-1 focus:ring-blue-300 rows-2"></textarea>
            <input v-model="newAdminNote.url" type="url" placeholder="主要網址 (選填)" class="border border-gray-300 p-2 w-full rounded text-sm mb-3 focus:ring-1 focus:ring-blue-300">
            
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
              <button @click="addAdminNote" class="bg-gray-800 text-white px-5 py-2 rounded text-sm font-bold shadow hover:bg-gray-900 transition">新增私密紀錄</button>
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
                  <button @click="startEditAdminNote(item)" class="text-blue-500 hover:text-blue-700 underline font-bold">編輯</button>
                  <button @click="deleteAdminNote(item.id)" class="text-red-500 hover:text-red-700 underline font-bold">刪除</button>
                </div>
              </div>
              
              <h5 :class="['text-lg font-bold mb-1', item.is_important ? 'text-red-700' : 'text-gray-900']">{{ item.title }}</h5>
              <p class="text-sm text-gray-600 whitespace-pre-line flex-1">{{ item.description }}</p>
              
              <div class="mt-3 flex flex-wrap gap-2">
                <a v-if="item.url" :href="item.url" target="_blank" :class="[themeObj.bg, 'text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-sm hover:opacity-80 transition-opacity']">主要網址 🚀</a>
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

      <section class="border-b pb-6">
        <h3 class="text-xl font-semibold mb-4 flex items-center gap-2">📝 管理員暫存清單 <span class="text-xs text-gray-400 font-normal border px-2 py-1 rounded">僅限後台可見</span></h3>
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
          <li v-if="todosList.length === 0" class="text-sm text-gray-400 py-4 text-center bg-gray-50 rounded-lg border border-dashed border-gray-300">
            目前沒有任何待辦或暫存訊息。
          </li>
        </ul>
      </section>

      <section class="border-b pb-6">
        <h3 class="text-xl font-semibold mb-4">📢 編輯前台教學內容</h3>
        <div class="bg-gray-50 p-4 rounded-xl border border-gray-200 mb-6">
          <h4 class="font-bold text-gray-700 mb-3">✨ 發布新公告到前台</h4>
          <div class="space-y-4">
            <div class="flex flex-col md:flex-row gap-3">
              <div class="md:w-1/3">
                <label class="block text-sm text-gray-600 mb-1">所屬科目</label>
                <select v-model="newPost.category" :class="['border border-gray-300 p-2 w-full rounded bg-white focus:ring-2 focus:border-transparent focus:outline-none', themeObj.ring]">
                  <option value="資訊科技">💻 資訊科技</option>
                  <option value="英語">🔤 英語</option>
                </select>
              </div>
              <div class="flex-1">
                <label class="block text-sm text-gray-600 mb-1">教學標題 (必填)</label>
                <input v-model="newPost.title" type="text" placeholder="輸入標題..." :class="['border border-gray-300 p-2 w-full rounded focus:ring-2 focus:border-transparent focus:outline-none', themeObj.ring]">
              </div>
            </div>
            
            <div class="flex gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="newPost.is_pinned" type="checkbox" class="w-4 h-4 text-blue-600 rounded">
                <span class="text-sm font-bold text-yellow-600">📌 置頂此公告</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="newPost.is_important" type="checkbox" class="w-4 h-4 text-red-600 rounded">
                <span class="text-sm font-bold text-red-600">🔥 標記為重要</span>
              </label>
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
                <option value="資訊科技">💻 資訊科技</option>
                <option value="英語">🔤 英語</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-xs text-gray-500 mb-1">標題</label>
              <input v-model="editingPost.title" type="text" class="border border-gray-300 p-2 w-full rounded text-sm">
            </div>
          </div>

          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="editingPost.is_pinned" type="checkbox" class="w-4 h-4 text-blue-600 rounded">
              <span class="text-sm font-bold text-yellow-600">📌 置頂</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="editingPost.is_important" type="checkbox" class="w-4 h-4 text-red-600 rounded">
              <span class="text-sm font-bold text-red-600">🔥 重要</span>
            </label>
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

        <ul v-else class="space-y-3 max-h-[500px] overflow-y-auto pr-2">
          <li v-for="item in adminBulletins" :key="item.id" class="flex flex-col md:flex-row justify-between md:items-center bg-white p-3 rounded-lg border shadow-sm hover:shadow-md transition-shadow" :class="item.is_important ? 'border-red-300 bg-red-50' : 'border-gray-200'">
            <div class="flex flex-col mb-2 md:mb-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span v-if="item.is_pinned" class="bg-yellow-400 text-white text-[10px] px-1.5 py-0.5 rounded">📌</span>
                <span v-if="item.is_important" class="bg-red-500 text-white text-[10px] px-1.5 py-0.5 rounded">🔥</span>
                <span :class="item.category === '資訊科技' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'" class="text-xs font-bold px-2 py-0.5 rounded whitespace-nowrap">{{ item.category }}</span>
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
        </ul>
      </section>

      <section class="border-b pb-6">
        <div class="flex flex-col md:flex-row justify-between md:items-center mb-4 gap-3">
          <h3 class="text-xl font-semibold">外部網站保活與捷徑設定</h3>
          <div class="flex gap-2">
            <button @click="pingUrlsByPlatform('Vercel')" :disabled="isPinging" class="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-900 disabled:opacity-50 transition duration-300 flex items-center shadow-sm text-sm">
              <span v-if="isPingingPlatform === 'Vercel'" class="animate-pulse">⏳ Vercel 喚醒中...</span>
              <span v-else>🚀 喚醒所有 Vercel</span>
            </button>
            <button @click="pingUrlsByPlatform('Render')" :disabled="isPinging" class="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:opacity-50 transition duration-300 flex items-center shadow-sm text-sm">
              <span v-if="isPingingPlatform === 'Render'" class="animate-pulse">⏳ Render 喚醒中...</span>
              <span v-else>🛸 喚醒所有 Render</span>
            </button>
          </div>
        </div>
        
        <p v-if="pingResult" :class="[themeObj.text, 'text-sm mb-3 font-bold']">{{ pingResult }}</p>

        <div class="flex flex-col md:flex-row gap-2 mb-6 bg-gray-50 p-3 rounded-lg border border-gray-200">
          <select v-model="newKeepAlive.platform" :class="['border border-gray-300 p-2 rounded text-sm bg-white focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
            <option value="Vercel">Vercel 專案</option>
            <option value="Render">Render 專案</option>
          </select>
          <input v-model="newKeepAlive.name" type="text" placeholder="網站名稱" :class="['border border-gray-300 p-2 w-full md:w-32 rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
          <input v-model="newKeepAlive.url" type="url" placeholder="喚醒 API 網址 (必填)" :class="['border border-gray-300 p-2 flex-1 rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
          <input v-model="newKeepAlive.home_url" type="url" placeholder="首頁網址 (選填)" :class="['border border-gray-300 p-2 flex-1 rounded text-sm focus:outline-none focus:ring-2 focus:border-transparent', themeObj.ring]">
          <button @click="addKeepAliveUrl" :class="[themeObj.bg, themeObj.hover, 'text-white px-5 py-2 rounded text-sm font-medium whitespace-nowrap shadow-sm']">新增</button>
        </div>

        <div class="space-y-6">
          <div>
            <h4 class="text-sm font-bold text-gray-500 mb-2 uppercase tracking-wider">▲ Vercel 專案</h4>
            <ul class="space-y-2">
              <li v-for="item in vercelUrls" :key="item.id" class="flex flex-col md:flex-row justify-between md:items-center bg-white p-3 rounded-lg border-l-4 border-l-gray-800 border-gray-200 shadow-sm">
                <div class="flex flex-col mb-2 md:mb-0">
                  <span class="font-bold text-gray-800">{{ item.name }}</span>
                  <div class="flex flex-col md:flex-row md:items-center gap-2 mt-1">
                    <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded truncate max-w-xs md:max-w-md">⚡ API: {{ item.url }}</span>
                    <a v-if="item.home_url" :href="item.home_url" target="_blank" :class="['inline-flex items-center justify-center text-xs font-bold bg-opacity-10 hover:bg-opacity-20 px-3 py-1 rounded-md w-fit', themeObj.text, themeObj.bg.replace('bg-', 'bg-').replace('600', '100')]">🔗 首頁</a>
                  </div>
                </div>
                <button @click="deleteKeepAliveUrl(item.id)" class="text-red-500 hover:bg-red-500 hover:text-white text-sm px-3 py-1 rounded border border-transparent hover:border-red-600 transition-colors self-end md:self-auto">刪除</button>
              </li>
            </ul>
          </div>
          <div>
            <h4 class="text-sm font-bold text-purple-500 mb-2 uppercase tracking-wider">◆ Render 專案</h4>
            <ul class="space-y-2">
              <li v-for="item in renderUrls" :key="item.id" class="flex flex-col md:flex-row justify-between md:items-center bg-white p-3 rounded-lg border-l-4 border-l-purple-500 border-gray-200 shadow-sm">
                <div class="flex flex-col mb-2 md:mb-0">
                  <span class="font-bold text-gray-800">{{ item.name }}</span>
                  <div class="flex flex-col md:flex-row md:items-center gap-2 mt-1">
                    <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded truncate max-w-xs md:max-w-md">⚡ API: {{ item.url }}</span>
                    <a v-if="item.home_url" :href="item.home_url" target="_blank" :class="['inline-flex items-center justify-center text-xs font-bold bg-opacity-10 hover:bg-opacity-20 px-3 py-1 rounded-md w-fit', themeObj.text, themeObj.bg.replace('bg-', 'bg-').replace('600', '100')]">🔗 首頁</a>
                  </div>
                </div>
                <button @click="deleteKeepAliveUrl(item.id)" class="text-red-500 hover:bg-red-500 hover:text-white text-sm px-3 py-1 rounded border border-transparent hover:border-red-600 transition-colors self-end md:self-auto">刪除</button>
              </li>
            </ul>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getTodayPassword } from '@/utils/auth'
import { themeConfig } from '@/utils/theme'

const dayjs = useDayjs()
const supabase = useSupabaseClient()

const currentTheme = useState('currentTheme')
const themeObj = computed(() => themeConfig[currentTheme.value] || themeConfig.purple)

const isAuthenticated = ref(false)
const inputPassword = ref('')
const errorMsg = ref('')

const siteTitle = ref('')
const marqueeText = ref('')
const siteTheme = ref('purple')
const siteSortOrder = ref('newest') 

// ====== 後台私密分頁變數 ======
const adminTabs = ref([])
const activeAdminTab = ref(null)
const newAdminTabName = ref('')
const adminNotes = ref([])
const getEmptyAdminNote = () => ({ title: '', description: '', url: '', is_important: false, is_pinned: false, links: [] })
const newAdminNote = ref(getEmptyAdminNote())
const editingAdminNote = ref(null)

// 根據目前選擇的 Tab 過濾並排序私密內容
const filteredAdminNotes = computed(() => {
  if (!activeAdminTab.value || !adminNotes.value) return []
  return adminNotes.value
    .filter(n => n.tab_id === activeAdminTab.value)
    .sort((a, b) => {
      if (a.is_pinned !== b.is_pinned) return a.is_pinned ? -1 : 1
      return new Date(b.created_at) - new Date(a.created_at) // 預設最新在前
    })
})

const todosList = ref([])
const newTodo = ref({ content: '', url: '', due_date: '' })

const getEmptyPost = () => ({ title: '', description: '', url: '', category: '資訊科技', is_important: false, is_pinned: false, links: [] })
const newPost = ref(getEmptyPost()) 
const adminBulletins = ref([]) 
const editingPost = ref(null)  

const showRenderToast = ref(false)
const visitorLogs = ref([])
const keepAliveUrls = ref([])
const newKeepAlive = ref({ name: '', url: '', home_url: '', platform: 'Vercel' })
const isPinging = ref(false)
const isPingingPlatform = ref('')
const pingResult = ref('')

const vercelUrls = computed(() => keepAliveUrls.value.filter(item => item.platform === 'Vercel' || !item.platform))
const renderUrls = computed(() => keepAliveUrls.value.filter(item => item.platform === 'Render'))

const login = () => {
  const correctPassword = getTodayPassword()
  if (inputPassword.value === correctPassword) {
    isAuthenticated.value = true
    errorMsg.value = ''
    loadSettings()
    loadAdminTabs()  // 載入私密分頁
    loadAdminNotes() // 載入私密內容
    loadBulletins() 
    loadTodos() 
    loadKeepAliveUrls()
    loadVisitorLogs()
  } else {
    errorMsg.value = '密碼錯誤！'
  }
}

const logout = () => {
  isAuthenticated.value = false
  inputPassword.value = ''
  navigateTo('/') 
}

const loadSettings = async () => {
  const { data } = await supabase.from('site_settings').select('*').eq('id', 1).single()
  if (data) {
    siteTitle.value = data.title
    marqueeText.value = data.marquee_text
    siteTheme.value = data.theme || 'purple'
    siteSortOrder.value = data.sort_order || 'newest'
    currentTheme.value = siteTheme.value
  }
}

const updateSettings = async () => {
  if (!siteTitle.value || !marqueeText.value) return alert('名稱與跑馬燈必填！')
  await supabase.from('site_settings').upsert({ id: 1, title: siteTitle.value, marquee_text: marqueeText.value, theme: siteTheme.value, sort_order: siteSortOrder.value })
  currentTheme.value = siteTheme.value 
  alert('設定已更新！')
}

// ====== 私密分頁邏輯 ======
const loadAdminTabs = async () => {
  const { data } = await supabase.from('admin_tabs').select('*').order('created_at', { ascending: true })
  if (data) {
    adminTabs.value = data
    if (data.length > 0 && !activeAdminTab.value) activeAdminTab.value = data[0].id // 預設選第一個
  }
}

const addAdminTab = async () => {
  if (!newAdminTabName.value) return alert('請輸入分頁名稱')
  const { data, error } = await supabase.from('admin_tabs').insert([{ name: newAdminTabName.value }]).select().single()
  if (!error && data) {
    newAdminTabName.value = ''
    await loadAdminTabs()
    activeAdminTab.value = data.id // 自動切換到新分頁
  }
}

const deleteAdminTab = async (id) => {
  if (!confirm('確定刪除此分頁？這會同時刪除裡面「所有」的內容喔！')) return
  await supabase.from('admin_tabs').delete().eq('id', id)
  if (activeAdminTab.value === id) activeAdminTab.value = null
  loadAdminTabs()
  loadAdminNotes()
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

// ====== To-Do 與 前台公告邏輯 ======
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

const loadBulletins = async () => {
  const { data } = await supabase.from('bulletins').select('*').order('is_pinned', { ascending: false }).order('created_at', { ascending: false })
  if (data) adminBulletins.value = data
}
const addPost = async () => {
  if (!newPost.value.title || !newPost.value.url) return alert('標題與網址必填！')
  await supabase.from('bulletins').insert([{ ...newPost.value }])
  alert('發布成功！')
  newPost.value = getEmptyPost()
  loadBulletins() 
}
const deletePost = async (id) => {
  if (!confirm('確定刪除？')) return
  await supabase.from('bulletins').delete().eq('id', id)
  loadBulletins()
}
const startEdit = (post) => { editingPost.value = JSON.parse(JSON.stringify({ ...post, links: post.links || [] })) }
const cancelEdit = () => { editingPost.value = null }
const saveEdit = async () => {
  if (!editingPost.value.title || !editingPost.value.url) return alert('標題與網址必填！')
  const { id, title, description, url, category, is_important, is_pinned, links } = editingPost.value
  await supabase.from('bulletins').update({ title, description, url, category, is_important, is_pinned, links }).eq('id', id)
  alert('更新成功！')
  editingPost.value = null 
  loadBulletins() 
}

const addLinkToObj = (obj) => {
  if (!obj.links) obj.links = []
  obj.links.push({ name: '', url: '' })
}
const removeLinkFromObj = (obj, index) => { obj.links.splice(index, 1) }

const loadVisitorLogs = async () => {
  const { data } = await supabase.from('visitor_logs').select('*').order('visited_at', { ascending: false }).limit(10)
  if (data) visitorLogs.value = data
}
const formatDate = (dateString) => dayjs(dateString).format('YYYY/MM/DD HH:mm')

const loadKeepAliveUrls = async () => {
  const { data } = await supabase.from('keep_alive_urls').select('*').order('created_at', { ascending: false })
  if (data) keepAliveUrls.value = data
}
const addKeepAliveUrl = async () => {
  if (!newKeepAlive.value.name || !newKeepAlive.value.url) return alert('必填！')
  await supabase.from('keep_alive_urls').insert([{ ...newKeepAlive.value }])
  newKeepAlive.value = { name: '', url: '', home_url: '', platform: 'Vercel' }
  loadKeepAliveUrls()
}
const deleteKeepAliveUrl = async (id) => {
  if (!confirm('確定刪除？')) return
  await supabase.from('keep_alive_urls').delete().eq('id', id)
  loadKeepAliveUrls()
}
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const pingUrlsByPlatform = async (platform) => {
  const targetUrls = platform === 'Vercel' ? vercelUrls.value : renderUrls.value
  if (targetUrls.length === 0) return
  isPinging.value = true
  isPingingPlatform.value = platform
  pingResult.value = ''
  let successCount = 0
  for (const item of targetUrls) {
    try {
      const urlObj = new URL(item.url)
      urlObj.searchParams.append('_ping_ts', Date.now().toString())
      await fetch(urlObj.toString(), { method: 'GET', mode: 'no-cors', cache: 'no-store' })
      successCount++
      await delay(300) 
    } catch (error) { console.error(`喚醒失敗:`, error) }
  }
  isPinging.value = false
  isPingingPlatform.value = ''
  pingResult.value = `${platform} 喚醒完成！成功發送 ${successCount}/${targetUrls.length} 個請求。`
  setTimeout(() => { pingResult.value = '' }, 4000)

  if (platform === 'Render') {
    setTimeout(() => {
      showRenderToast.value = true
      setTimeout(() => { showRenderToast.value = false }, 10000)
    }, 60000) 
  }
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce-in {
  0% { transform: translateY(150%); opacity: 0; }
  50% { transform: translateY(-10%); }
  100% { transform: translateY(0); opacity: 1; }
}
.animate-bounce-in { animation: bounce-in 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
</style>