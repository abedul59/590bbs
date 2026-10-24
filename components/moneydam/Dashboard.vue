<template>
  <div class="moneydam-page py-4 px-3">
    <div class="moneydam-shell card border-0 shadow-lg mx-auto overflow-hidden">
      <header class="moneydam-header text-white text-center p-4">
        <h1 class="h3 fw-bold mb-2">💧 六大水庫資金流向分析</h1>
        <p class="mb-0 opacity-75">總體資金在股市、外匯、債券、原物料、銀行與房地產之間的流向監測</p>
      </header>

      <div class="card-body p-3 p-md-4">
        <div class="row g-3 bg-light border rounded-3 p-3 mb-4">
          <div class="col-md-6">
            <label class="form-label small fw-bold text-secondary">匯入新分析（JSON）</label>
            <input type="file" accept=".json" class="form-control" @change="handleFileUpload">
          </div>
          <div class="col-md-6">
            <label class="form-label small fw-bold text-secondary">歷史紀錄</label>
            <select v-model="selectedRecordId" class="form-select font-monospace" @change="displaySelectedRecord">
              <option value="" disabled>-- 選擇報告 --</option>
              <option v-for="record in records" :key="record.id" :value="record.id">{{ record.timestamp }}</option>
            </select>
          </div>
        </div>

        <div class="text-center mb-4">
          <button class="btn btn-success rounded-pill fw-bold px-5 py-3 shadow" :disabled="isScraping" @click="triggerCloudScraper">
            <span v-if="isScraping" class="spinner-border spinner-border-sm me-2" />
            {{ isScraping ? '雲端爬蟲執行中…' : '☁️ 一鍵啟動雲端自動分析' }}
          </button>
          <p v-if="status" class="small fw-bold mt-3 mb-0" :class="status.startsWith('❌') ? 'text-danger' : 'text-success'">{{ status }}</p>
        </div>

        <div v-if="currentContent" class="d-flex justify-content-center gap-2 mb-4">
          <button class="btn btn-sm fw-bold" :class="viewMode === 'gui' ? 'btn-success' : 'btn-outline-secondary'" @click="viewMode = 'gui'">📊 視覺儀表板</button>
          <button class="btn btn-sm fw-bold" :class="viewMode === 'text' ? 'btn-success' : 'btn-outline-secondary'" @click="viewMode = 'text'">📝 原始文字</button>
        </div>

        <div v-if="loading" class="text-center py-5"><div class="spinner-border text-success" /><p class="text-muted mt-2">讀取紀錄中…</p></div>
        <div v-else-if="!currentContent" class="text-center text-muted py-5"><div class="display-5 mb-2">🗃️</div><p>請執行雲端分析、上傳 JSON 或選擇歷史紀錄。</p></div>

        <div v-else-if="viewMode === 'gui' && parsedData" class="row g-3">
          <div v-for="item in parsedData.reservoirs" :key="item.name" class="col-md-6">
            <article class="reservoir-card h-100 p-3 border rounded-4 shadow-sm" :class="item.isGoodForStock ? 'good' : 'bad'">
              <div class="d-flex justify-content-between align-items-start gap-2">
                <h2 class="h5 fw-bold mb-0"><span class="fs-3 me-2">{{ item.icon }}</span>{{ item.name }}</h2>
                <span class="badge" :class="item.isGoodForStock ? 'bg-success' : 'bg-danger'">{{ item.status.split('(')[0] }}</span>
              </div>
              <div class="bg-light rounded-3 p-3 mt-3"><p class="font-monospace small mb-2 text-break">{{ item.value }}</p><p class="small text-muted fst-italic mb-0">{{ item.status }}</p></div>
            </article>
          </div>
          <div class="col-12"><section class="conclusion rounded-4 p-4 text-center"><h2 class="h4 fw-bold">🎯 綜合判定結論</h2><p class="mb-0 fw-semibold">{{ parsedData.conclusion }}</p></section></div>
        </div>

        <pre v-else class="raw-report bg-dark text-success rounded-3 p-4 small">{{ currentContent }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const records = ref([])
const selectedRecordId = ref('')
const currentContent = ref('')
const status = ref('')
const viewMode = ref('gui')
const isScraping = ref(false)
const loading = ref(false)

const parsedData = computed(() => {
  if (!currentContent.value) return null
  const lines = currentContent.value.split('\n')
  const extract = (keyword) => {
    const result = { value: '無數據', status: '未知狀態', isGoodForStock: false }
    const start = lines.findIndex(line => line.includes(keyword))
    if (start < 0) return result
    for (let offset = 0; offset <= 10 && start + offset < lines.length; offset += 1) {
      const line = lines[start + offset]
      if (!line.includes('| 判定:')) continue
      const [value, state] = line.split('| 判定:')
      result.value = value.replace(/\[水庫.*?\]/g, '').replace(/->/g, '').trim()
      result.status = String(state || '').trim() || '未知狀態'
      result.isGoodForStock = result.status.includes('釋放') || result.status.includes('未吸金')
      break
    }
    return result
  }
  const conclusionIndex = lines.findIndex(line => line.includes('【資金流向綜合判定】'))
  const conclusion = conclusionIndex >= 0 ? lines.slice(conclusionIndex + 1, conclusionIndex + 3).map(line => line.trim()).filter(Boolean).join(' ') : '暫無結論數據'
  return {
    reservoirs: [
      { name: '外匯市場', icon: '💵', ...extract('[水庫二：外匯市場]') },
      { name: '債券市場', icon: '📜', ...extract('[水庫三：債券市場]') },
      { name: '原物料與通膨', icon: '🛢️', ...extract('[水庫四：原物料/通膨]') },
      { name: '央行與銀行', icon: '🏦', ...extract('[水庫五：央行與銀行體系]') },
      { name: '房地產市場', icon: '🏠', ...extract('[水庫六：房地產市場]') }
    ], conclusion
  }
})

const fetchRecords = async (selectNewest = false) => {
  loading.value = true
  try {
    const response = await $fetch('/api/moneydam/records')
    records.value = response.records || []
    if (records.value.length && (selectNewest || !selectedRecordId.value)) {
      selectedRecordId.value = records.value[0].id
      currentContent.value = records.value[0].content
    }
  } catch (error) {
    status.value = `❌ 讀取失敗：${error?.data?.message || error.message}`
  } finally {
    loading.value = false
  }
}

const displaySelectedRecord = () => {
  const record = records.value.find(item => item.id === selectedRecordId.value)
  if (record) currentContent.value = record.content
}

const handleFileUpload = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async loadEvent => {
    try {
      status.value = '⏳ 上傳中…'
      const json = JSON.parse(String(loadEvent.target?.result || ''))
      await $fetch('/api/moneydam/upload', { method: 'POST', body: json })
      status.value = '✅ 手動上傳成功'
      event.target.value = ''
      await fetchRecords(true)
    } catch (error) {
      status.value = `❌ 上傳失敗：${error?.data?.message || error.message}`
    }
  }
  reader.readAsText(file)
}

const triggerCloudScraper = async () => {
  isScraping.value = true
  status.value = '⏳ 正在啟動 Moneydam 雲端爬蟲，約需 15～60 秒…'
  try {
    const response = await $fetch('/api/moneydam/trigger', { method: 'POST' })
    status.value = `✅ 更新完成（${response.storage}）`
    await fetchRecords(true)
  } catch (error) {
    status.value = `❌ 執行失敗：${error?.data?.message || error.message}`
  } finally {
    isScraping.value = false
  }
}

onMounted(() => fetchRecords())
</script>

<style scoped>
.moneydam-page { min-height: calc(100vh - 62px); background: #f1f5f9; }
.moneydam-shell { max-width: 960px; }
.moneydam-header { background: linear-gradient(135deg, #059669, #0f766e); }
.reservoir-card { border-left-width: 5px !important; background: #fff; }
.reservoir-card.good { border-left-color: #10b981 !important; }
.reservoir-card.bad { border-left-color: #f43f5e !important; }
.conclusion { color: #312e81; border: 1px solid #c7d2fe; background: linear-gradient(135deg, #eef2ff, #dbeafe); }
.raw-report { max-height: 65vh; overflow: auto; white-space: pre-wrap; }
</style>
