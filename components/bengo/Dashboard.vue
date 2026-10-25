<template>
  <div class="bengo-page">
    <div class="bengo-shell">
      <div v-if="message" class="notice" :class="`notice-${messageType}`">{{ message }}</div>

      <section class="control-card">
        <div class="control-block">
          <label>🔍 股票代碼</label>
          <div class="input-row">
            <input v-model.trim="searchQuery" placeholder="例如 2330" @keyup.enter="fetchStockData">
            <button class="primary" :disabled="loading" @click="fetchStockData">查詢</button>
            <button class="warning" :disabled="scraping" @click="triggerCloudScrape">
              {{ scraping ? '雲端抓取中…' : '⚡ 雲端抓取' }}
            </button>
          </div>
          <button class="link-button" @click="showList = !showList">
            {{ showList ? '隱藏清單' : '📂 顯示已匯入清單' }}
          </button>
        </div>

        <div class="control-block">
          <label for="bengo-json">📁 匯入 Bengo JSON</label>
          <div class="input-row">
            <input id="bengo-json" ref="fileInput" type="file" accept=".json,application/json" @change="selectFile">
            <button class="success" :disabled="uploading || !selectedFile" @click="uploadJson">
              {{ uploading ? '匯入中…' : '匯入' }}
            </button>
          </div>
        </div>
      </section>

      <section v-if="showList" class="data-card">
        <h2>📂 已匯入股票</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>股票代碼</th><th>股票名稱</th><th>最新日期</th><th>操作</th></tr></thead>
            <tbody>
              <tr v-for="stock in summary" :key="stock.stock_id">
                <td><strong>{{ stock.stock_id }}</strong></td>
                <td>{{ stock.stock_name }}</td>
                <td>{{ stock.latest_date }}</td>
                <td><button class="small primary" @click="quickSearch(stock.stock_id)">查看走勢</button></td>
              </tr>
              <tr v-if="!summary.length"><td colspan="4" class="empty">目前尚無資料</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <template v-if="records.length && !showList">
        <section class="data-card chart-card">
          <h2>{{ searchQuery }} {{ stockName }}</h2>
          <Line :data="chartData" :options="chartOptions" />
        </section>
        <section class="data-card">
          <h2>📊 詳細歷史數據</h2>
          <div class="table-wrap history-table">
            <table>
              <thead><tr><th>日期</th><th>收盤價</th><th>門檻</th><th>大戶人數</th><th>大戶持股</th><th>備註</th></tr></thead>
              <tbody>
                <tr v-for="row in records" :key="`${row.stock_id}-${row.date}`">
                  <td>{{ row.date }}</td><td>{{ row.price }}</td><td>{{ row.bengo_threshold }}</td>
                  <td>{{ row.major_people }}</td><td class="major">{{ row.major_pct }}%</td><td>{{ row.note }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Line } from 'vue-chartjs'
import { CategoryScale, Chart as ChartJS, Filler, Legend, LineElement, LinearScale, PointElement, Title, Tooltip } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const searchQuery = ref('')
const records = ref([])
const summary = ref([])
const showList = ref(false)
const loading = ref(false)
const scraping = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)
const fileInput = ref(null)
const message = ref('')
const messageType = ref('info')
let pollTimer = null

const stockName = computed(() => records.value[0]?.stock_name || '')
const setMessage = (text, type = 'info') => {
  message.value = text
  messageType.value = type
}

const fetchSummary = async () => {
  try {
    const response = await $fetch('/api/bengo/data')
    summary.value = response.summary || []
  } catch (error) {
    setMessage(`股票清單讀取失敗：${error?.data?.statusMessage || error.message}`, 'danger')
  }
}

const fetchStockData = async ({ quiet = false } = {}) => {
  if (!searchQuery.value) {
    if (!quiet) setMessage('請先輸入股票代碼', 'warning')
    return []
  }
  loading.value = true
  try {
    const response = await $fetch('/api/bengo/data', { params: { stock_id: searchQuery.value } })
    records.value = response.records || []
    summary.value = response.summary || []
    if (records.value.length) {
      showList.value = false
      if (!quiet) setMessage(`已載入 ${records.value.length} 筆資料`, 'success')
    } else if (!quiet) {
      setMessage(`找不到 ${searchQuery.value}，可使用雲端抓取或匯入 JSON。`, 'warning')
    }
    return records.value
  } catch (error) {
    if (!quiet) setMessage(`查詢失敗：${error?.data?.statusMessage || error.message}`, 'danger')
    return []
  } finally {
    loading.value = false
  }
}

const quickSearch = async (stockId) => {
  searchQuery.value = String(stockId)
  await fetchStockData()
}

const triggerCloudScrape = async () => {
  if (!searchQuery.value) return setMessage('請先輸入股票代碼', 'warning')
  scraping.value = true
  const before = JSON.stringify(records.value)
  try {
    const response = await $fetch('/api/bengo/trigger', { method: 'POST', body: { stock_id: searchQuery.value } })
    setMessage(`已由 ${new URL(response.endpoint).hostname} 接受任務，等待資料回傳…`, 'info')
    let attempts = 0
    clearInterval(pollTimer)
    pollTimer = setInterval(async () => {
      attempts += 1
      const latest = await fetchStockData({ quiet: true })
      if (JSON.stringify(latest) !== before) {
        clearInterval(pollTimer)
        scraping.value = false
        setMessage('🎉 雲端抓取與同步完成', 'success')
        await fetchSummary()
      } else if (attempts >= 30) {
        clearInterval(pollTimer)
        scraping.value = false
        setMessage('等待結束；資料可能已是最新狀態，或爬蟲仍在處理。', 'warning')
      }
    }, 3000)
  } catch (error) {
    scraping.value = false
    setMessage(`雲端抓取失敗：${error?.data?.statusMessage || error.message}`, 'danger')
  }
}

const selectFile = event => { selectedFile.value = event.target.files?.[0] || null }
const uploadJson = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    const json = JSON.parse(await selectedFile.value.text())
    const response = await $fetch('/api/bengo/upload', { method: 'POST', body: json })
    searchQuery.value = String(json.stock_id || '')
    setMessage(`成功匯入 ${response.count} 筆資料`, 'success')
    await fetchStockData({ quiet: true })
    await fetchSummary()
  } catch (error) {
    setMessage(`匯入失敗：${error?.data?.statusMessage || error.message}`, 'danger')
  } finally {
    uploading.value = false
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
  }
}

const chartData = computed(() => {
  const rows = [...records.value].reverse().slice(-180)
  return {
    labels: rows.map(row => row.date),
    datasets: [
      { label: '大戶持股比例 (%)', data: rows.map(row => row.major_pct), borderColor: '#dc2626', backgroundColor: '#dc262619', yAxisID: 'percentage', fill: true, tension: .3, pointRadius: 2 },
      { label: '股價', data: rows.map(row => row.price), borderColor: '#2563eb', yAxisID: 'price', borderDash: [5, 5], tension: .3, pointRadius: 2 },
      { label: '大戶人數', data: rows.map(row => row.major_people), borderColor: '#059669', yAxisID: 'people', tension: .3, pointRadius: 2 }
    ]
  }
})

const chartOptions = {
  responsive: true,
  interaction: { mode: 'index', intersect: false },
  scales: {
    percentage: { type: 'linear', position: 'left', min: 0, max: 100, title: { display: true, text: '持股 %' } },
    price: { type: 'linear', position: 'left', grid: { drawOnChartArea: false }, title: { display: true, text: '股價' } },
    people: { type: 'linear', position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: '大戶人數' } }
  }
}

onMounted(fetchSummary)
onBeforeUnmount(() => clearInterval(pollTimer))
</script>

<style scoped>
.bengo-page { min-height: calc(100vh - 62px); padding: 1.5rem; background: #f1f5f9; }
.bengo-shell { width: min(1180px, 100%); margin: auto; }
.notice { margin-bottom: 1rem; padding: .9rem 1rem; border-radius: .7rem; font-weight: 700; }
.notice-info { color: #1e40af; background: #dbeafe; }.notice-success { color: #166534; background: #dcfce7; }
.notice-warning { color: #92400e; background: #fef3c7; }.notice-danger { color: #991b1b; background: #fee2e2; }
.control-card { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.5rem; margin-bottom: 1.25rem; padding: 1.25rem; border-radius: 1rem; background: #fff; box-shadow: 0 8px 25px #0f172a12; }
.control-block label { display: block; margin-bottom: .55rem; color: #475569; font-weight: 800; }
.input-row { display: flex; gap: .5rem; }.input-row input { min-width: 0; flex: 1; padding: .65rem .75rem; border: 1px solid #cbd5e1; border-radius: .55rem; }
button { border: 0; border-radius: .55rem; padding: .65rem .9rem; font-weight: 800; cursor: pointer; } button:disabled { cursor: not-allowed; opacity: .55; }
.primary { color: #fff; background: #2563eb; }.warning { color: #422006; background: #fbbf24; }.success { color: #fff; background: #16a34a; }
.link-button { float: right; margin-top: .55rem; padding: .3rem; color: #475569; background: transparent; }.small { padding: .35rem .65rem; }
.data-card { margin-bottom: 1.25rem; padding: 1.25rem; border-radius: 1rem; background: #fff; box-shadow: 0 8px 25px #0f172a12; }.data-card h2 { margin: 0 0 1rem; font-size: 1.2rem; font-weight: 900; }
.chart-card { min-height: 420px; }.table-wrap { overflow: auto; border: 1px solid #e2e8f0; border-radius: .7rem; }.history-table { max-height: 520px; }
table { width: 100%; border-collapse: collapse; text-align: center; } th { color: #fff; background: #1f2937; } th, td { padding: .7rem; border-bottom: 1px solid #e2e8f0; white-space: nowrap; } tbody tr:nth-child(even) { background: #f8fafc; }.major { color: #dc2626; font-weight: 800; }.empty { padding: 2rem; color: #64748b; }
@media (max-width: 800px) { .control-card { grid-template-columns: 1fr; }.input-row { flex-wrap: wrap; }.input-row input { flex-basis: 100%; } }
</style>
