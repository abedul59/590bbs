<template>
  <div class="tracker-dashboard container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3 flex-wrap gap-3">
      <div>
        <h1 class="tracker-title mb-1">📈 台股資金流向儀表板</h1>
        <small class="text-muted">上市、上櫃、興櫃類股平均與成交額 Top 30</small>
      </div>
      <div class="d-flex align-items-center gap-3 flex-wrap">
        <button class="btn btn-primary fw-bold shadow-sm" :disabled="isScraping" @click="triggerCloudScrape">
          <span v-if="isScraping" class="spinner-border spinner-border-sm me-1" />
          {{ isScraping ? '雲端同步中…' : '🚀 觸發雲端即時同步' }}
        </button>
        <div v-if="availableDates.length" class="d-flex align-items-center gap-2">
          <label class="fw-bold text-nowrap text-secondary">📅 歷史：</label>
          <select v-model="selectedDate" class="form-select w-auto fw-bold text-primary" @change="loadData(selectedDate)">
            <option v-for="date in availableDates" :key="date" :value="date">{{ formatDisplayDate(date) }}</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="status" class="alert" :class="status.startsWith('❌') ? 'alert-danger' : 'alert-info'">{{ status }}</div>
    <div v-if="!availableDates.length && !loading" class="alert alert-warning text-center fw-bold">目前尚無資料，請執行雲端同步。</div>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary" /><p class="mt-2 text-muted">讀取資料中…</p></div>

    <div v-else-if="statsData.length || top30Data.length" class="card shadow-sm border-0 overflow-hidden">
      <div class="tabs-header d-flex border-bottom bg-light">
        <button class="tab-btn" :class="{ active: mainTab === 'categories' }" @click="mainTab = 'categories'">📊 類股平均數據</button>
        <button class="tab-btn" :class="{ active: mainTab === 'top30' }" @click="mainTab = 'top30'">🔥 成交額 Top 30</button>
      </div>

      <div v-if="mainTab === 'categories'" class="p-3">
        <div class="d-flex justify-content-center gap-2 mb-3 flex-wrap">
          <button v-for="market in ['上市', '上櫃', '興櫃']" :key="market" class="btn btn-sm fw-bold px-4" :class="marketTab === market ? activeMarketClass(market) : outlineMarketClass(market)" @click="marketTab = market">{{ market }}類股</button>
        </div>
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-dark"><tr><th>市場</th><th>類股名稱</th><th>平均漲跌幅</th><th>平均股價</th><th class="text-end">平均成交量（張）</th></tr></thead>
            <tbody>
              <tr v-for="stat in filteredStats" :key="`${stat.market}-${stat.category}`">
                <td><span class="badge" :class="badgeClass(stat.market)">{{ stat.market }}</span></td>
                <td class="fw-bold">{{ stat.category }}</td>
                <td :class="String(stat.avg_change_pct).includes('-') ? 'text-success fw-bold' : 'text-danger fw-bold'">{{ stat.avg_change_pct }}</td>
                <td>{{ stat.avg_price }}</td><td class="text-end">{{ stat.avg_vol }}</td>
              </tr>
              <tr v-if="!filteredStats.length"><td colspan="5" class="text-center text-muted py-4">此市場目前無資料</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="p-3">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-warning"><tr><th>排名</th><th>市場</th><th>代碼</th><th>名稱</th><th class="text-end">估算成交金額（千元）</th></tr></thead>
            <tbody><tr v-for="stock in top30Data" :key="`${stock.rank}-${stock.ticker}`"><td><span class="badge bg-dark">#{{ stock.rank }}</span></td><td><span class="badge" :class="badgeClass(stock.market)">{{ stock.market }}</span></td><td>{{ stock.ticker }}</td><td class="fw-bold">{{ stock.name }}</td><td class="text-end fw-bold text-danger">{{ stock.total_value }}</td></tr></tbody>
          </table>
        </div>
      </div>
      <div class="card-footer small text-muted">資料時間：{{ formatDisplayDate(selectedDate) }}｜儲存來源：{{ dataSource }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const mainTab = ref('categories')
const marketTab = ref('上市')
const statsData = ref([])
const top30Data = ref([])
const availableDates = ref([])
const selectedDate = ref('')
const loading = ref(false)
const isScraping = ref(false)
const status = ref('')
const dataSource = ref('-')

const formatDisplayDate = value => {
  const text = String(value || '')
  return /^\d{14}$/.test(text) ? `${text.slice(0, 4)}-${text.slice(4, 6)}-${text.slice(6, 8)} ${text.slice(8, 10)}:${text.slice(10, 12)}:${text.slice(12, 14)}` : text
}
const badgeClass = market => ({ 上市: 'bg-danger', 上櫃: 'bg-primary', 興櫃: 'bg-success' }[market] || 'bg-secondary')
const activeMarketClass = market => ({ 上市: 'btn-danger', 上櫃: 'btn-primary', 興櫃: 'btn-success' }[market])
const outlineMarketClass = market => ({ 上市: 'btn-outline-danger', 上櫃: 'btn-outline-primary', 興櫃: 'btn-outline-success' }[market])
const filteredStats = computed(() => statsData.value.filter(row => row.market === marketTab.value))

const loadData = async (date = '') => {
  loading.value = true
  try {
    const response = await $fetch('/api/twstocktracker/data', { params: date ? { date } : {} })
    availableDates.value = response.availableDates || []
    selectedDate.value = response.selectedDate || ''
    statsData.value = response.stats || []
    top30Data.value = response.top30 || []
    dataSource.value = response.source || '-'
  } catch (error) {
    status.value = `❌ 讀取失敗：${error?.data?.message || error.message}`
  } finally {
    loading.value = false
  }
}

const triggerCloudScrape = async () => {
  isScraping.value = true
  status.value = '⏳ 正在呼叫雲端爬蟲，約需 20～60 秒…'
  try {
    const response = await $fetch('/api/twstocktracker/trigger', { method: 'POST' })
    status.value = `✅ ${response.message}`
    await loadData(response.date)
  } catch (error) {
    status.value = `❌ ${error?.data?.message || error.message}`
  } finally {
    isScraping.value = false
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.tracker-dashboard { max-width: 1080px; font-family: "Microsoft JhengHei", sans-serif; }
.tracker-title { color: #243447; font-weight: 900; }
.tab-btn { flex: 1; padding: 1rem; border: 0; color: #6c757d; background: transparent; font-weight: 800; }
.tab-btn.active { color: #212529; border-bottom: 4px solid #ff9800; background: #fff; }
</style>
