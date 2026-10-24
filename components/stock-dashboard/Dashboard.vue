<template>
  <div class="stock-dashboard bg-light min-vh-100 pb-5">
    <nav class="navbar navbar-dark bg-dark mb-4 shadow-sm">
      <div class="container">
        <span class="navbar-brand">📈 總大六大指標和本益比區間分析</span>
      </div>
    </nav>

    <div class="container">
      <div class="row mb-4 g-3">
        <div class="col-lg-6">
          <div class="card card-shadow h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="card-title text-primary fw-bold mb-0">🔍 查詢股票</h6>
                <button type="button" class="btn btn-outline-secondary btn-sm shadow-sm" data-bs-toggle="modal" data-bs-target="#stockListModal">
                  📋 已匯入名單
                </button>
              </div>

              <div class="row g-2 align-items-center mb-3">
                <div class="col-3">
                  <select v-model="searchQuery.year" class="form-select form-select-sm">
                    <option value="">年份</option>
                    <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
                  </select>
                </div>
                <div class="col-3">
                  <select v-model="searchQuery.month" class="form-select form-select-sm">
                    <option value="">月份</option>
                    <option v-for="m in monthOptions" :key="m" :value="m">{{ m }}月</option>
                  </select>
                </div>
                <div class="col-4">
                  <input v-model="searchQuery.id" type="text" class="form-control form-control-sm" placeholder="股票代碼">
                </div>
                <div class="col-2">
                  <button @click="fetchStockData" class="btn btn-primary btn-sm w-100 fw-bold">查詢</button>
                </div>
              </div>

              <div class="row g-2 align-items-center pt-2 border-top">
                <div class="col-8">
                  <small class="text-muted">若資料庫無資料，可即時呼叫雲端爬蟲：</small>
                </div>
                <div class="col-4">
                  <button @click="callCloudApi" class="btn btn-warning btn-sm w-100 fw-bold shadow-sm" :disabled="isFetchingApi">
                    <span v-if="isFetchingApi" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    {{ isFetchingApi ? '爬蟲中...' : '☁️ 雲端分析' }}
                  </button>
                </div>
              </div>

            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="card card-shadow h-100">
            <div class="card-body">
              <h6 class="card-title text-success fw-bold mb-3">📂 上傳數據 (手動 JSON)</h6>
              <div class="row g-2 align-items-center">
                <div class="col-9">
                  <input type="file" @change="onFileSelected" class="form-control form-control-sm" accept=".json">
                </div>
                <div class="col-3">
                  <button @click="uploadFile" class="btn btn-success btn-sm w-100 fw-bold" :disabled="isUploading">
                    {{ isUploading ? '上傳中...' : '上傳' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="stockData" class="card card-shadow mb-5 animate__animated animate__fadeIn">
        <div class="card-header bg-white py-3 d-flex justify-content-between align-items-center flex-wrap">
          <h4 class="mb-0 fw-bold text-dark">
            <span class="badge bg-primary me-2">{{ stockData.stock_id }}</span>{{ stockData.stock_name }}
          </h4>
          <small class="text-muted mt-2 mt-md-0">
            基準日: {{ metaData.QueryDate }} ({{ stockData.data_year }} / {{ stockData.data_month }})
          </small>
        </div>

        <div class="card-body p-4">
          <div class="row g-3 mb-4 text-center">
            <div class="col-6 col-md-2"><div class="p-2 border rounded bg-light stat-card" style="border-left-color: #0d6efd !important;"><small class="text-muted d-block mb-1">最新成交</small><span class="fs-5 fw-bold">{{ perData.Now_Price }}</span></div></div>
            <div class="col-6 col-md-2"><div class="p-2 border rounded bg-light stat-card"><small class="text-muted d-block mb-1">預估營收</small><span class="fs-5">{{ perData.Predict_Rev }}</span></div></div>
            <div class="col-6 col-md-2"><div class="p-2 border rounded bg-light stat-card" style="border-left-color: #dc3545 !important;"><small class="text-muted d-block mb-1">{{ forecastYear }} 預估EPS</small><span class="fs-4 text-danger fw-bold">{{ forwardValuation.eps }}</span></div></div>
            <div class="col-6 col-md-2"><div class="p-2 border rounded bg-light stat-card"><small class="text-muted d-block mb-1">{{ forecastYear }} 目標價(高)</small><span class="fs-5 text-success fw-bold">{{ forwardValuation.targetH }}</span></div></div>
            <div class="col-6 col-md-2"><div class="p-2 border rounded bg-light stat-card"><small class="text-muted d-block mb-1">{{ forecastYear }} 目標價(低)</small><span class="fs-5 text-secondary fw-bold">{{ forwardValuation.targetL }}</span></div></div>
            <div class="col-6 col-md-2"><div class="p-2 border rounded bg-light stat-card"><small class="text-muted d-block mb-1">潛在報酬</small><span class="fs-5 text-danger fw-bold">{{ perData.Profit }}</span></div></div>
          </div>

          <ul class="nav nav-tabs nav-fill mb-4" id="stockTabs" role="tablist">
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-sim">🧪 模擬試算</button></li>
            <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-hist">歷史股價</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-rev">營收</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-net">淨利</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-six">六大指標</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-q4">Q4 檢查</button></li>
          </ul>

          <div class="tab-content" id="stockTabsContent">
            <div class="tab-pane fade" id="tab-sim">
              <div class="row g-4">
                <div class="col-lg-5">
                  <div class="card h-100 border-0 bg-light">
                    <div class="card-body">
                      <h5 class="card-title text-secondary fw-bold mb-3 border-bottom pb-2">📊 原始預估 (JSON)</h5>
                      <ul class="list-group list-group-flush bg-transparent mb-3">
                        <li class="list-group-item bg-transparent d-flex justify-content-between px-0"><span>{{ forecastYear }} 預估 EPS</span><strong class="text-dark">{{ forwardValuation.eps }}</strong></li>
                        <li class="list-group-item bg-transparent d-flex justify-content-between px-0"><span>原始預估營收</span><strong>{{ perData.Predict_Rev }} 億</strong></li>
                        <li class="list-group-item bg-transparent d-flex justify-content-between px-0"><span>原始營收年增率</span><strong>{{ perData.YoY_Use }}</strong></li>
                        <li class="list-group-item bg-transparent d-flex justify-content-between px-0"><span>平均淨利率</span><strong>{{ perData.Net_Avg }}</strong></li>
                        <li class="list-group-item bg-transparent d-flex justify-content-between px-0"><span>股本</span><strong>{{ perData.Capital }} 億</strong></li>
                      </ul>
                      <div class="p-3 rounded note-box">
                        <h6 class="fw-bold text-dark border-bottom border-warning pb-2 mb-2">💡 說明</h6>
                        <p class="small text-muted mb-0">程式會先反推「基期營收」，再依據您輸入的成長率與淨利率重新計算 EPS。<br><em>(基期營收 × 新成長率 × 新淨利率) ÷ 股本</em></p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="col-lg-7">
                  <div class="card border-primary shadow-sm">
                    <div class="card-header bg-primary text-white fw-bold">✏️ 手動調整參數 (即時連動計算)</div>
                    <div class="card-body">
                      <div class="row g-3 mb-3">
                        <div class="col-md-6">
                          <label class="form-label small fw-bold">營收年增率 (%)</label>
                          <div class="input-group">
                            <input type="number" step="any" v-model="simInputs.yoy" class="form-control">
                            <span class="input-group-text">%</span>
                          </div>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small fw-bold">稅後淨利率 (%)</label>
                          <div class="input-group">
                            <input type="number" step="any" v-model="simInputs.net" class="form-control">
                            <span class="input-group-text">%</span>
                          </div>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small fw-bold">本益比 (高)</label>
                          <input type="number" step="any" v-model="simInputs.peH" class="form-control">
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small fw-bold">本益比 (低)</label>
                          <input type="number" step="any" v-model="simInputs.peL" class="form-control">
                        </div>
                      </div>

                      <div class="mt-4 pt-3 border-top">
                        <div class="alert alert-info d-flex justify-content-between align-items-center mb-3">
                          <span>模擬計算 EPS</span>
                          <span class="h3 mb-0 fw-bold text-primary">{{ simRes.calc_eps }}</span>
                        </div>
                        <div class="row text-center mb-3">
                          <div class="col-4 border-end">
                            <small class="text-muted">目標價(高)</small>
                            <div class="fw-bold text-success">{{ simRes.target_h }}</div>
                            <small class="text-success">{{ simRes.upside }}</small>
                          </div>
                          <div class="col-4 border-end">
                            <small class="text-muted">即時價 (爬蟲)</small>
                            <div class="fw-bold text-dark">{{ simRes.live_price }}</div>
                          </div>
                          <div class="col-4">
                            <small class="text-muted">目標價(低)</small>
                            <div class="fw-bold text-danger">{{ simRes.target_l }}</div>
                            <small class="text-danger">{{ simRes.downside }}</small>
                          </div>
                        </div>
                        <div class="text-center mb-3">
                          <span class="badge bg-dark rounded-pill px-3 py-2">風險報酬比 (RR): {{ simRes.rr }}</span>
                        </div>

                        <div class="accordion" id="calcAccordion">
                          <div class="accordion-item border-0">
                            <h2 class="accordion-header">
                              <button class="accordion-button collapsed bg-light py-2 text-muted small" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne">
                                👁️ 查看詳細計算過程 (驗證用)
                              </button>
                            </h2>
                            <div id="collapseOne" class="accordion-collapse collapse" data-bs-parent="#calcAccordion">
                              <div class="accordion-body p-0">
                                <table class="table table-sm table-bordered mb-0 small text-center">
                                  <thead class="table-light"><tr><th>步驟</th><th>結果</th></tr></thead>
                                  <tbody>
                                    <tr v-for="row in simRes.details" :key="row.step">
                                      <td>{{ row.step }}<br><small class="text-muted font-monospace">{{ row.formula }}</small></td>
                                      <td class="fw-bold align-middle">{{ row.result }}</td>
                                    </tr>
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="tab-pane fade show active" id="tab-hist">
              <div class="alert alert-info py-2 small">
                <strong>{{ forecastYear }} 本益比區間：</strong>
                預估 EPS {{ forwardValuation.eps }} × 歷史 PE
                （高 {{ perData.PE_Use_H }}／低 {{ perData.PE_Use_L }}）＝
                目標價 {{ forwardValuation.targetL }}～{{ forwardValuation.targetH }}。
              </div>
              <div class="table-responsive">
                <table class="table table-bordered table-striped text-center align-middle">
                  <thead class="table-dark"><tr><th>年份</th><th>最高</th><th>最低</th><th>EPS</th><th>PE 高</th><th>PE 低</th></tr></thead>
                  <tbody>
                    <tr class="table-warning fw-bold">
                      <td>{{ forecastYear }}/{{ forecastYearRoc }}(預估)</td>
                      <td class="text-danger">{{ forwardValuation.targetH }}</td><td class="text-success">{{ forwardValuation.targetL }}</td>
                      <td class="text-primary">{{ forwardValuation.eps }}</td><td>-</td><td>-</td>
                    </tr>
                    <tr v-for="(row, index) in histRows" :key="index">
                      <td>{{ row.year_str }} <span v-if="index === 0 && perData.EPS1_Is_Est">(預)</span></td>
                      <td>{{ row.h }}</td><td>{{ row.l }}</td><td>{{ row.eps }}</td><td>{{ row.pe_h }}</td><td>{{ row.pe_l }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="tab-pane fade" id="tab-rev">
              <div class="row"><div class="col-md-8 mx-auto">
                <table class="table table-sm table-bordered text-center">
                  <thead class="table-light"><tr><th>月份</th><th>營收(億)</th><th>年增率</th></tr></thead>
                  <tbody>
                    <tr v-for="row in revRows" :key="'rev'+row.name"><td>{{ row.name }}</td><td>{{ row.val }}</td><td>-</td></tr>
                    <tr class="table-secondary"><td>---</td><td></td><td></td></tr>
                    <tr v-for="row in yoyRows" :key="'yoy'+row.name"><td>{{ row.name }}</td><td>-</td><td :class="row.yoy.includes('-') ? 'text-success' : 'text-danger'">{{ row.yoy }}</td></tr>
                  </tbody>
                </table>
              </div></div>
            </div>

            <div class="tab-pane fade" id="tab-net">
              <div class="row"><div class="col-md-6 mx-auto">
                <table class="table table-bordered text-center">
                  <thead class="table-light"><tr><th>季度</th><th>淨利率</th></tr></thead>
                  <tbody>
                    <tr v-for="row in netRows" :key="row.name"><td>{{ row.name }}</td><td>{{ row.val }}</td></tr>
                  </tbody>
                </table>
              </div></div>
            </div>

            <div class="tab-pane fade" id="tab-six">
              <div class="alert alert-info text-center mb-3"><strong>🏆 總評分：</strong> <span class="fs-4 fw-bold text-danger">{{ sixData.Average }}</span> 分</div>
              <div class="row g-3">
                <div class="col-md-4 col-sm-6" v-for="(item, key) in sixData" :key="key" v-show="key !== 'Name' && key !== 'Average'">
                  <div class="card h-100 card-shadow">
                    <div class="card-header d-flex justify-content-between small">
                      <strong>{{ key }}</strong>
                      <span class="badge" :class="['A', 'AA'].includes(item.Rating) ? 'bg-danger' : 'bg-secondary'">{{ item.Rating }}</span>
                    </div>
                    <div class="card-body p-0">
                      <table class="table table-sm table-striped mb-0 text-center">
                        <thead><tr><th>項目</th><th>數值</th></tr></thead>
                        <tbody><tr v-for="(d, i) in item.Data" :key="i"><td>{{ d.Name }}</td><td>{{ d.Val }}</td></tr></tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="tab-pane fade" id="tab-q4">
              <div class="row"><div class="col-md-8 mx-auto">
                <table class="table table-bordered table-hover text-center">
                  <thead class="table-dark"><tr><th>項目</th><th>數值 / 狀態</th></tr></thead>
                  <tbody>
                    <tr v-for="(row, index) in q4Rows" :key="index">
                      <td class="fw-bold">{{ row.label }}</td><td>{{ row.val }}</td>
                    </tr>
                  </tbody>
                </table>
              </div></div>
            </div>

          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="stockListModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header bg-light">
            <h5 class="modal-title fw-bold text-dark">📋 資料庫已有股票</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-0">
            <div v-if="availableStocks.length > 0" class="list-group list-group-flush">
              <a href="#" v-for="stock in availableStocks" :key="stock.id" @click.prevent="selectStockFromModal(stock.id)" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                <span><strong class="text-primary me-2">{{ stock.id }}</strong> {{ stock.name }}</span>
                <span class="badge bg-secondary rounded-pill text-white">點擊帶入</span>
              </a>
            </div>
            <div v-else class="text-center text-muted p-4">目前資料庫尚無任何股票，請先上傳 JSON 數據。</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useHead } from '#imports'

// 載入 Bootstrap JS 讓 Modal 與 Tabs 生效
useHead({
  script: [{ src: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js', tagPosition: 'bodyClose' }]
})

// === 狀態管理 ===
const searchQuery = ref({ id: '', year: '', month: '' })
const stockData = ref(null)
const perData = ref({})
const metaData = ref({})
const sixData = ref({})
const livePrice = ref(null)
const availableStocks = ref([])
const selectedFile = ref(null)
const isUploading = ref(false)
const isFetchingApi = ref(false) // 控制雲端 API 按鈕狀態
const simInputs = ref({ yoy: 0, net: 0, peH: 0, peL: 0 })

// 🚀 ⚠️ 這裡替換成您在 Hugging Face 建立的 API 網址！
const HF_API_URL = "https://lawxstudents168-PER-api.hf.space/api/analyze"

// 產生年份 (2026~2036) 與月份 (1~12) 下拉選單選項
const yearOptions = Array.from({ length: 11 }, (_, i) => 2026 + i)
const monthOptions = Array.from({ length: 12 }, (_, i) => i + 1)

// === 輔助函式：解析百分比 ===
const parsePct = (val) => {
  if (!val) return 0;
  return parseFloat(String(val).replace('%', '').replace(',', '').trim()) / 100 || 0;
}

// 新資料直接使用 Python 輸出的估值年度；舊資料則依資料日期與基準月份相容推算。
const forecastYear = computed(() => {
  const explicitYear = Number(perData.value.Forecast_Year)
  if (explicitYear > 0) return explicitYear

  const queryDate = String(metaData.value.QueryDate || '')
  const [dateYear, dateMonth] = queryDate.split('-').map(Number)
  const currentYear = Number(perData.value.Current_Year) || dateYear || new Date().getFullYear()
  const targetMonth = Number(metaData.value.TargetMonth || stockData.value?.data_month || 0)
  const effectiveMonth = Math.max(dateMonth || 0, targetMonth)
  return currentYear + (effectiveMonth >= 9 ? 1 : 0)
})

const forecastYearRoc = computed(() => {
  const explicitYear = Number(perData.value.Forecast_Year_ROC)
  return explicitYear > 0 ? explicitYear : forecastYear.value - 1911
})

// 舊 JSON 的營收已外推到下一年，但 EPS/目標價仍停在當年；顯示時即時修正。
const forwardValuation = computed(() => {
  const per = perData.value
  let eps = Number(per.Predict_EPS || 0)
  const currentYear = Number(per.Current_Year || forecastYear.value)
  const isLegacyNextYear = !Number(per.Forecast_Year) && forecastYear.value > currentYear
  if (isLegacyNextYear) {
    const revenue = Number(per.Predict_Rev || 0)
    const margin = parsePct(per.Net_Avg)
    const capital = Number(per.Capital || 0)
    if (revenue > 0 && margin !== 0 && capital > 0) {
      eps = Number(((revenue * margin / capital) * 10).toFixed(2))
    }
  }

  const peH = Number(per.PE_Use_H || 0)
  const peL = Number(per.PE_Use_L || 0)
  const shouldRecalculateTargets = isLegacyNextYear && eps > 0
  return {
    eps,
    targetH: shouldRecalculateTargets ? Number((eps * peH).toFixed(2)) : Number(per.Target_H || 0),
    targetL: shouldRecalculateTargets ? Number((eps * peL).toFixed(2)) : Number(per.Target_L || 0)
  }
})

// === API：獲取初始股票清單 ===
const fetchAvailableStocks = async () => {
  try {
    const res = await $fetch('/api/stock-dashboard/stock')
    if (res && res.availableStocks) {
      availableStocks.value = res.availableStocks
    }
  } catch (err) {
    console.error("無法取得股票清單", err)
  }
}

onMounted(() => {
  fetchAvailableStocks()
})

// === Modal 點擊帶入 ===
const selectStockFromModal = (stockId) => {
  searchQuery.value.id = stockId
  fetchStockData()
  document.querySelector('#stockListModal .btn-close')?.click()
}

// === API：上傳檔案 ===
const onFileSelected = (event) => {
  selectedFile.value = event.target.files[0]
}

const uploadFile = async () => {
  if (!selectedFile.value) { return alert('請先選擇 JSON 檔案！') }
  isUploading.value = true
  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const json = JSON.parse(e.target.result)
      const res = await $fetch('/api/stock-dashboard/upload', { method: 'POST', body: json })
      if (res && res.success) {
        alert(res.message)
        fetchAvailableStocks()
        const firstKey = Object.keys(json)[0]
        if (firstKey) {
          searchQuery.value.id = firstKey
          fetchStockData()
        }
      }
    } catch (err) {
      alert('上傳發生錯誤！')
    } finally {
      isUploading.value = false
    }
  }
  reader.readAsText(selectedFile.value)
}

// === API：查詢資料庫股票 ===
const fetchStockData = async () => {
  if (!searchQuery.value.id) return alert('請輸入股票代碼')
  try {
    const res = await $fetch('/api/stock-dashboard/stock', { params: searchQuery.value })
    if (res.currentData) {
      stockData.value = res.currentData
      perData.value = res.currentData.raw_data?.PER_Analysis || {}
      sixData.value = res.currentData.raw_data?.Six_Indicators || {}
      metaData.value = res.currentData.raw_data?.Meta || {}

      // 初始化模擬參數
      simInputs.value.yoy = parseFloat((perData.value.YoY_Use || '0').replace('%', ''))
      simInputs.value.net = parseFloat((perData.value.Net_Avg || '0').replace('%', ''))
      simInputs.value.peH = parseFloat(perData.value.PE_Use_H || 0)
      simInputs.value.peL = parseFloat(perData.value.PE_Use_L || 0)

      // 抓即時股價
      livePrice.value = null
      const priceRes = await $fetch('/api/stock-dashboard/live-price', { params: { id: searchQuery.value.id } })
      livePrice.value = priceRes.price
    } else {
      alert('資料庫中找不到該股票資料，請使用【雲端分析】即時抓取！')
      stockData.value = null
    }
  } catch (err) {
    alert('讀取資料失敗')
  }
}

// === API：呼叫 Hugging Face 爬蟲並直接存入 DB ===
const callCloudApi = async () => {
  const sid = searchQuery.value.id
  const targetMonth = searchQuery.value.month || new Date().getMonth() + 1

  if (!sid) return alert('請先輸入股票代碼！')

  isFetchingApi.value = true
  try {
    // 1. 呼叫 Hugging Face API 進行爬蟲
    const hfResponse = await $fetch(HF_API_URL, {
      method: 'POST',
      body: { stock_id: sid, target_month: parseInt(targetMonth) }
    })

    if (hfResponse && hfResponse.success && hfResponse.data) {
      // 2. 爬蟲成功，將收到的 JSON 直接傳給 Nuxt 自己的上傳 API 寫入 Supabase
      const uploadRes = await $fetch('/api/stock-dashboard/upload', {
        method: 'POST',
        body: hfResponse.data
      })

      if (uploadRes && uploadRes.success) {
        alert(`✅ 雲端分析完成！已將 ${sid} 存入資料庫。`)
        fetchAvailableStocks() // 更新清單
        fetchStockData()       // 自動顯示剛抓下來的數據
      } else {
        alert('爬蟲成功，但寫入資料庫失敗。')
      }
    } else {
      alert('Hugging Face 爬蟲 API 回傳失敗。')
    }
  } catch (err) {
    console.error(err)
    alert(`雲端爬蟲發生錯誤，請確認 HF_API_URL 設定是否正確：${err.message}`)
  } finally {
    isFetchingApi.value = false
  }
}

// === 計算屬性 ===

// 1. 模擬試算 (含詳細算式)
const simRes = computed(() => {
  if (!stockData.value) return {}
  const per = perData.value
  const origYoy = parsePct(per.YoY_Use)
  const origNet = parsePct(per.Net_Avg)
  const capital = parseFloat(per.Capital || 1)
  const origRevPredict = parseFloat(per.Predict_Rev || 0)

  const details = []

  const suppliedBaseRev = parseFloat(per.Forecast_Base_Revenue || 0)
  const isNextYearForecast = per.Forecast_Horizon === 'next_year' || forecastYear.value > Number(per.Current_Year || forecastYear.value)
  const usesSuppliedBase = isNextYearForecast && suppliedBaseRev > 0
  const baseRev = usesSuppliedBase
    ? suppliedBaseRev
    : ((1 + origYoy) !== 0 ? origRevPredict / (1 + origYoy) : origRevPredict)
  details.push({ step: `1. ${forecastYear.value - 1} 基期營收`, formula: usesSuppliedBase ? `程式補齊的完整年度營收` : `預估營收 ${origRevPredict} ÷ (1 + 原始YoY ${(origYoy*100).toFixed(2)}%)`, result: `${baseRev.toFixed(2)} 億` })

  const simYoy = simInputs.value.yoy / 100
  const simNet = simInputs.value.net / 100
  const simPeH = simInputs.value.peH || 0
  const simPeL = simInputs.value.peL || 0

  const simRev = baseRev * (1 + simYoy)
  details.push({ step: `2. ${forecastYear.value} 模擬營收`, formula: `基期 ${baseRev.toFixed(2)} × (1 + 設定YoY ${(simYoy*100).toFixed(2)}%)`, result: `${simRev.toFixed(2)} 億` })

  const simNetIncome = simRev * simNet
  details.push({ step: "3. 模擬淨利", formula: `營收 ${simRev.toFixed(2)} × 設定淨利率 ${(simNet*100).toFixed(2)}%`, result: `${simNetIncome.toFixed(2)} 億` })

  const simEps = Number(((simNetIncome / capital) * 10).toFixed(2))
  details.push({ step: "4. 模擬 EPS", formula: `(淨利 ${simNetIncome.toFixed(2)} ÷ 股本 ${capital}) × 10`, result: `${simEps} 元` })

  const targetH = Number((simEps * simPeH).toFixed(2))
  const targetL = Number((simEps * simPeL).toFixed(2))
  details.push({ step: "5. 目標價", formula: `高: EPS ${simEps} × PE ${simPeH} | 低: EPS ${simEps} × PE ${simPeL}`, result: `高 ${targetH} / 低 ${targetL}` })

  let upside = 0, downside = 0, rr = 0
  const lp = livePrice.value
  if (lp) {
    upside = (targetH - lp) / lp
    downside = (targetL - lp) / lp
    rr = downside !== 0 ? Math.abs(upside / downside) : 0
    details.push({ step: "6. 報酬與風險", formula: `即時價 ${lp} vs 目標價 ${targetH} / ${targetL}`, result: `上 ${(upside*100).toFixed(2)}% / 下 ${(downside*100).toFixed(2)}%` })
  }

  return {
    live_price: lp || "抓取失敗", calc_eps: simEps, calc_rev: simRev.toFixed(2), target_h: targetH, target_l: targetL,
    upside: lp ? `${(upside*100).toFixed(2)}%` : "-", downside: lp ? `${(downside*100).toFixed(2)}%` : "-", rr: lp ? rr.toFixed(2) : "-", details
  }
})

// 2. 歷史股價 Table
const histRows = computed(() => {
  const per = perData.value
  if (!per.H) return []
  const rows = []
  const loopLen = Math.min(per.H.length, per.L?.length||0, per.EPS?.length||0)
  const cYear = per.Current_Year || new Date().getFullYear()
  const cYearRoc = per.Current_Year_ROC || (cYear - 1911)
  for(let i=0; i<loopLen; i++) {
    rows.push({ year_str: `${cYear - 1 - i}/${cYearRoc - 1 - i}`, h: per.H[i], l: per.L[i], eps: per.EPS[i], pe_h: per.PE_H?.[i] || '-', pe_l: per.PE_L?.[i] || '-' })
  }
  return rows
})

// 3. 營收 Table
const revRows = computed(() => (perData.value.Rev_Names || []).map((name, i) => ({ name, val: perData.value.Rev_Vals[i] })))
const yoyRows = computed(() => (perData.value.YoY_Names || []).map((name, i) => ({ name, yoy: perData.value.YoY_Vals[i] })))

// 4. 淨利 Table
const netRows = computed(() => (perData.value.Net_Names || []).map((name, i) => ({ name, val: perData.value.Net_Vals[i] })))

// 5. Q4 檢查 Table (套用動態季別名稱修正)
const q4Rows = computed(() => {
  const per = perData.value
  const q1 = per.EPS_Q1 || 0, q2 = per.EPS_Q2 || 0, q3 = per.EPS_Q3 || 0
  return [
    { label: "狀態", val: per.Detect_Reason || '-' },
    { label: "網頁最新季別", val: per.Latest_Quarter_Str || '-' },
    { label: `${per.epsq1N || '最新季'} EPS (實際)`, val: q1 },
    { label: `${per.epsq2N || '前一季'} EPS (實際)`, val: q2 },
    { label: `${per.epsq3N || '前二季'} EPS (實際)`, val: q3 },
    { label: "前三筆 EPS 總和", val: Number((q1 + q2 + q3).toFixed(2)) },
    { label: "---", val: "---" },
    { label: "去年 Q4 營收", val: per.Q4_Rev_Actual || 0 },
    { label: "平均淨利率", val: per.Net_Avg || '0%' },
    { label: "股本(億)", val: per.Capital || 0 },
    { label: "Q4 EPS (估算)", val: per.Q4_EPS_Est || 0 },
    { label: "---", val: "---" },
    { label: "最近全年 EPS (估/實)", val: per.Total_EPS_Est || 0 },
    { label: "---", val: "---" },
    { label: "估值年度", val: `${forecastYear.value}/${forecastYearRoc.value}` },
    { label: `${forecastYear.value} 預估營收`, val: per.Predict_Rev || 0 },
    { label: `${forecastYear.value} 預估 EPS`, val: forwardValuation.value.eps },
    { label: "預估方法", val: per.Forecast_Method || "預估營收 × 平均淨利率 ÷ 股本 × 10" }
  ]
})
</script>

<style scoped>
/* 完整還原原本的手機優化與排版 CSS */
.table-sm td, .table-sm th { padding: 0.3rem; font-size: 0.9rem; }
.nav-tabs .nav-link { color: #495057; cursor: pointer; }
.nav-tabs .nav-link.active { background-color: #0d6efd; color: white !important; font-weight: bold; border-color: #0d6efd; }
.stat-card { transition: all 0.2s; border-left: 4px solid transparent; }
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
.card-shadow { box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: none; }
.input-group-text { background-color: #e9ecef; width: 45px; justify-content: center; }
.note-box { border-left: 4px solid #ffc107; background-color: #fff3cd; }
</style>
