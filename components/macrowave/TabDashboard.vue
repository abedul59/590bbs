<template>
  <div class="container mb-4">
    <div class="card shadow-sm mb-4 border-0">
      <div class="card-body">
        <div class="row align-items-center text-center">
            
            <div class="col-md-4 mb-3 mb-md-0">
                <h6 class="text-uppercase text-muted fw-bold mb-2" style="font-size: 0.8rem;">數據時間與歷史切換</h6>
                <div class="input-group input-group-sm justify-content-center">
                    <span class="input-group-text bg-light fw-bold">📅 紀錄</span>
                    <select class="form-select text-center fw-bold text-primary" v-model="selectedHistory" @change="onHistoryChange" :disabled="isSyncing || isLoading">
                        <option value="latest">最新戰情數據 (Latest)</option>
                        <option v-for="h in historyList" :key="h.filename" :value="h.filename">{{ h.label || h.filename }}</option>
                    </select>
                </div>
                <div class="mt-2 text-muted" style="font-size: 0.75rem;">來源: {{ dataSourceDisplay }}</div>
            </div>
            
            <div class="col-md-4 mb-3 mb-md-0 border-start border-end px-3">
                <div class="input-group input-group-sm mb-2 justify-content-center">
                    <span class="input-group-text bg-light fw-bold">伺服器</span>
                    <select class="form-select text-center fw-bold text-secondary" v-model="selectedSyncService" :disabled="isSyncing">
                        <option v-for="service in syncServices" :key="service.value" :value="service.value">{{ service.label }}</option>
                    </select>
                </div>
                <button class="btn btn-outline-danger btn-sm w-100 fw-bold" @click="triggerSync" :disabled="isSyncing">
                    <span v-if="isSyncing" class="spinner-border spinner-border-sm me-1"></span>
                    {{ syncStatusText }}
                </button>
            </div>

            <div class="col-md-4">
                <button class="btn btn-outline-success btn-sm w-100 fw-bold mb-2" data-bs-toggle="collapse" data-bs-target="#uploadBox">📤 手動上傳 JSON</button>
                <div class="collapse mt-2" id="uploadBox">
                    <div class="d-flex gap-1 justify-content-center flex-wrap">
                        <input type="file" @change="handleFileSelect" class="form-control form-control-sm" accept=".json">
                        <button @click="uploadToServer" class="btn btn-success btn-sm fw-bold w-100 mt-1" :disabled="!selectedFile || isUploading">
                            <span v-if="isUploading" class="spinner-border spinner-border-sm me-1"></span>{{ isUploading ? '上傳中...' : '確認上傳' }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <hr class="my-3 text-muted">
        <div class="row align-items-center g-3 text-center">
            <div class="col-md-3 text-md-end"><span class="fw-bold text-secondary">🔗 外部系統聯動：</span></div>
            <div class="col-md-4">
                <button class="btn btn-dark btn-sm w-100 fw-bold shadow-sm" @click="triggerTwstockSync" :disabled="isSyncingTwstock">
                    <span v-if="isSyncingTwstock" class="spinner-border spinner-border-sm me-1"></span>
                    {{ isSyncingTwstock ? '更新中...' : '🚀 獨立更新 Twstock168' }}
                </button>
            </div>
            <div class="col-md-5">
                <a href="https://www.macromicro.me/collections/46/tw-stock-relative/110457/tw-tmf-long-to-short-ratio-of-individual-player" target="_blank" class="btn btn-danger btn-sm w-100 fw-bold shadow-sm">🔥 微台散戶多空比 (M平方)</a>
            </div>
        </div>
      </div>
    </div>

    <div v-if="dashboardData">
        
        <div class="row">
            <div class="col-12 mb-4">
                <div class="card text-center p-4 bg-white shadow-sm border-0">
                    <h5 class="text-muted mb-3 text-uppercase fw-bold">Mark 17 總經風險評分</h5>
                    <div class="d-flex justify-content-center align-items-center gap-4 flex-wrap">
                        <div class="d-flex align-items-baseline">
                            <span class="display-3 fw-bold text-dark">{{ dashboardData.content.total_score }}</span>
                            <span class="text-muted fs-4 ms-2">/ 15</span>
                        </div>
                        <div :class="['advice-badge', 'advice-' + dashboardData.content.advice]">策略建議: {{ dashboardData.content.advice }}</div>
                    </div>
                </div>
            </div>

            <div class="col-lg-4 col-md-12 mb-4" v-if="dashboardData.content.us_jp_spread">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center fw-bold">
                        <span>📉 美日債券利差</span>
                        <small class="opacity-75 font-monospace">門檻: 2.0%</small>
                    </div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="text-muted fw-bold">🇺🇸 美債 10Y</span>
                            <span class="fw-bold fs-5">{{ dashboardData.content.us_jp_spread.us }}%</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span class="text-muted fw-bold">🇯🇵 日債 10Y</span>
                            <span class="fw-bold fs-5">{{ dashboardData.content.us_jp_spread.jp }}%</span>
                        </div>
                        <hr>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="fw-bold fs-5">利差 (Spread)</span>
                            <span :class="['fs-3 fw-bold', 'status-' + dashboardData.content.us_jp_spread.status]">{{ dashboardData.content.us_jp_spread.spread }}%</span>
                        </div>
                        <div v-if="dashboardData.content.us_jp_spread.spread < 2.0" class="alert alert-danger mt-3 mb-0 py-2 text-center fw-bold">
                            ⚠️ 警告：利差跌破 2%
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-4 col-md-12 mb-4">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-header bg-warning text-dark fw-bold d-flex justify-content-between align-items-center">
                        <span>🥇 貴金屬重挫偵測</span>
                        <small class="font-monospace">跌幅 > 50%</small>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-striped mb-0 align-middle text-center" style="font-size: 0.9rem;">
                                <thead class="table-light">
                                    <tr><th>商品</th><th>現價</th><th>跌幅</th><th>狀態</th></tr>
                                </thead>
                                <tbody>
                                    <tr v-for="metal in dashboardData.content.metals" :key="metal.name">
                                        <td class="fw-bold">{{ metal.name }}</td>
                                        <td class="font-monospace">{{ Math.round(metal.current) }}</td>
                                        <td class="text-muted font-monospace">{{ metal.drop ? metal.drop.toFixed(1) : 0 }}%</td>
                                        <td :class="'status-' + metal.status">{{ metal.status === 'Danger' ? '⚠️' : '✅' }}</td>
                                    </tr>
                                    <tr v-if="!dashboardData.content.metals?.length"><td colspan="4" class="text-muted py-3">暫無數據</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-4 col-md-12 mb-4">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-header bg-primary text-white fw-bold d-flex justify-content-between align-items-center bg-gradient">
                        <span>💱 關鍵匯率監控</span>
                        <small class="font-monospace">半年位階</small>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover mb-0 align-middle text-center" style="font-size: 0.9rem;">
                                <thead class="table-light">
                                    <tr><th>貨幣</th><th>現價</th><th>距高點</th><th>距低點</th></tr>
                                </thead>
                                <tbody>
                                    <tr v-for="curr in dashboardData.content.currencies" :key="curr.name">
                                        <td class="fw-bold text-start ps-3">{{ curr.name }}</td>
                                        <td class="fw-bold font-monospace">{{ curr.current }}</td>
                                        <td :class="curr.diff_high < -5 ? 'text-success fw-bold font-monospace' : 'text-muted font-monospace'">{{ curr.diff_high }}%</td>
                                        <td :class="curr.diff_low > 5 ? 'text-danger fw-bold font-monospace' : 'text-muted font-monospace'">{{ curr.diff_low }}%</td>
                                    </tr>
                                    <tr v-if="!dashboardData.content.currencies?.length"><td colspan="4" class="text-muted py-3">暫無數據</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="dashboardData.content.raw_indicators" class="row mt-2">
            <div class="col-12"><h4 class="mb-3 border-start border-5 border-primary ps-3 fw-bold">📑 整體經濟指標細項</h4></div>
            
            <div class="col-12 mb-3">
                <div class="card section-bar-tw shadow-sm border-0">
                    <div class="card-header bg-light fw-bold text-secondary">📌 核心概況 & 時間</div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-6 col-md-3"><div class="metric-item"><div class="metric-label">資料日期</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.Date || "--" }}</div></div></div>
                            <div class="col-6 col-md-3"><div class="metric-item"><div class="metric-label">Mark 17 得分</div><div class="metric-value text-primary font-monospace fs-4">{{ dashboardData.content.raw_indicators.Mark17_Score || "--" }}</div></div></div>
                            <div class="col-6 col-md-3"><div class="metric-item"><div class="metric-label">CRB 指數</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.CRB_Index || "--" }}</div></div></div>
                            <div class="col-6 col-md-3"><div class="metric-item"><div class="metric-label">美元指數 (DXY)</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.Currency_DXY || "--" }}</div></div></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-md-6 mb-3">
                <div class="card section-bar-tw shadow-sm h-100 border-0">
                    <div class="card-header bg-light fw-bold text-secondary">💰 台灣資金與股市</div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-6"><div class="metric-item"><div class="metric-label">台股總市值 (百萬)</div><div class="metric-value text-success font-monospace">{{ dashboardData.content.raw_indicators.MV_Num || "--" }}</div><div class="metric-sub text-muted small mt-1">{{ dashboardData.content.raw_indicators.MV_Date || "" }}</div></div></div>
                            <div class="col-6"><div class="metric-item"><div class="metric-label">市值貨幣比</div><div class="metric-value font-monospace fs-4">{{ dashboardData.content.raw_indicators.MV_Ratio || "--" }}</div></div></div>
                            <div class="col-6"><div class="metric-item"><div class="metric-label">M1B 年增率 (YoY)</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.M1b_YoY || "--" }}%</div></div></div>
                            <div class="col-6"><div class="metric-item"><div class="metric-label">M1B 數值 (億)</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.M1b_Num || "--" }}</div><div class="metric-sub text-muted small mt-1">{{ dashboardData.content.raw_indicators.M1b_Date || "" }}</div></div></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-md-6 mb-3">
                <div class="card section-bar-us shadow-sm h-100 border-0">
                    <div class="card-header bg-light fw-bold text-secondary">📉 美國債市與利率</div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-6"><div class="metric-item"><div class="metric-label">美債 10年殖利率</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.US_10Y || "--" }}%</div></div></div>
                            <div class="col-6"><div class="metric-item"><div class="metric-label">美債 3個月殖利率</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.US_3M || "--" }}%</div></div></div>
                            <div class="col-6"><div class="metric-item"><div class="metric-label">長短利差 (10Y-3M)</div><div :class="['metric-value font-monospace fs-4', dashboardData.content.raw_indicators.Spread_3M_10Y < 0 ? 'text-danger' : '']">{{ dashboardData.content.raw_indicators.Spread_3M_10Y || "--" }}</div></div></div>
                            <div class="col-6"><div class="metric-item"><div class="metric-label">衰退機率</div><div class="metric-value text-danger font-monospace fs-4">{{ dashboardData.content.raw_indicators.Recession_Prob || "--" }}</div><div class="metric-sub text-muted small mt-1">{{ dashboardData.content.raw_indicators.Recession_Date || "" }}</div></div></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-md-6 mb-3">
                <div class="card section-bar-cycle shadow-sm h-100 border-0">
                    <div class="card-header bg-light fw-bold text-secondary">🏭 景氣循環與製造業</div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-6"><div class="metric-item"><div class="metric-label">中國 PMI</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.China_PMI || "--" }}</div><div class="metric-sub text-muted small mt-1">{{ dashboardData.content.raw_indicators.China_PMI_Date || "" }}</div></div></div>
                            <div class="col-6"><div class="metric-item"><div class="metric-label">美國失業率</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.Unemployment || "--" }}%</div></div></div>
                            <div class="col-12"><div class="metric-item"><div class="metric-label">美國領先指標 (LEI)</div><div class="metric-value font-monospace fs-4">{{ dashboardData.content.raw_indicators.Leading_Index || "--" }}</div></div></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-md-6 mb-3">
                <div class="card section-bar-sentiment shadow-sm h-100 border-0">
                    <div class="card-header bg-light fw-bold text-secondary">🛍️ 消費信心與訂單</div>
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-6"><div class="metric-item"><div class="metric-label">密大消費者信心</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.Michigan_Index || "--" }}</div><div class="metric-sub text-muted small mt-1">{{ dashboardData.content.raw_indicators.Michigan_Date || "" }}</div></div></div>
                            <div class="col-6"><div class="metric-item"><div class="metric-label">耐久財新訂單 (YoY)</div><div class="metric-value font-monospace">{{ dashboardData.content.raw_indicators.Durable_YoY_New || "--" }}</div></div></div>
                            <div class="col-12"><div class="metric-item"><div class="metric-label">扣除國防耐久財 (YoY)</div><div class="metric-value font-monospace fs-4">{{ dashboardData.content.raw_indicators.Durable_YoY_Old || "--" }}</div></div></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-2" v-if="dashboardData.content.global_markets?.length">
            <div class="col-12">
                <div class="card shadow-sm border-0">
                    <div class="card-header bg-secondary text-white fw-bold d-flex justify-content-between align-items-center flex-wrap">
                        <span>🌍 全球主要股市位階偵測 (乖離率監控)</span>
                        <small class="mt-1 mt-md-0 font-monospace">負值代表回檔幅度，正值代表反彈幅度</small>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover table-bordered mb-0 align-middle text-center" style="font-size: 0.85rem; min-width: 800px;">
                                <thead class="table-light">
                                    <tr>
                                        <th rowspan="2" class="align-middle">指數名稱</th>
                                        <th rowspan="2" class="align-middle bg-light">現價</th>
                                        <th colspan="2">半年 (6M)</th>
                                        <th colspan="2">一年 (1Y)</th>
                                        <th colspan="2">三年 (3Y)</th>
                                    </tr>
                                    <tr>
                                        <th class="text-muted">距高點 %</th><th class="text-muted">距低點 %</th>
                                        <th class="text-muted">距高點 %</th><th class="text-muted">距低點 %</th>
                                        <th class="text-muted">距高點 %</th><th class="text-muted">距低點 %</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="m in dashboardData.content.global_markets" :key="m.name">
                                        <td class="fw-bold text-start ps-3">{{ m.name }}</td>
                                        <td class="fw-bold bg-light font-monospace">{{ m.current }}</td>
                                        <td :class="m['6M_High_Diff'] < -10 ? 'text-success fw-bold' : ''">{{ m['6M_High_Diff'] }}%</td>
                                        <td :class="m['6M_Low_Diff'] > 10 ? 'text-danger fw-bold' : ''">{{ m['6M_Low_Diff'] }}%</td>
                                        <td :class="m['1Y_High_Diff'] < -15 ? 'text-success fw-bold' : ''">{{ m['1Y_High_Diff'] }}%</td>
                                        <td :class="m['1Y_Low_Diff'] > 15 ? 'text-danger fw-bold' : ''">{{ m['1Y_Low_Diff'] }}%</td>
                                        <td :class="m['3Y_High_Diff'] < -20 ? 'text-success fw-bold' : ''">{{ m['3Y_High_Diff'] }}%</td>
                                        <td :class="m['3Y_Low_Diff'] > 20 ? 'text-danger fw-bold' : ''">{{ m['3Y_Low_Diff'] }}%</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card shadow-sm border-0">
                    <div class="card-header bg-dark text-white fw-bold d-flex justify-content-between cursor-pointer" data-bs-toggle="collapse" href="#mark17Details">
                        <span>📋 Mark 17 詳細計分表 (含原始數值與前值對照)</span>
                        <small>▼ 點擊展開/收合</small>
                    </div>
                    <div class="collapse show" id="mark17Details">
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0 align-middle">
                                    <thead class="table-light">
                                        <tr>
                                            <th>監測項目</th>
                                            <th class="text-center">數值 / 狀態</th>
                                            <th class="text-center">風險得分</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr v-for="item in dashboardData.content.mark17" :key="item.item">
                                            <td class="fw-bold text-dark">{{ item.item.replace(/PMI/g, '美國 PMI') }}</td>
                                            <td class="text-center">
                                                <div :class="['fw-bold fs-6 font-monospace', 'status-' + item.status]">{{ item.value }}</div>
                                                <div v-if="item.prev_value !== undefined && item.prev_value !== null" class="text-muted mt-1 font-monospace" style="font-size: 0.75rem;">
                                                    (前值: {{ item.prev_value }})
                                                </div>
                                            </td>
                                            <td class="text-center">
                                                <span v-if="item.score !== 0 && item.score !== '-'" class="badge bg-danger rounded-pill px-3 fs-6">
                                                    {{ typeof item.score === 'number' && item.score > 0 ? '+' + item.score : item.score }}
                                                </span>
                                                <span v-else class="text-muted text-opacity-50">-</span>
                                            </td>
                                        </tr>
                                        <tr v-if="!dashboardData.content.mark17?.length"><td colspan="3" class="text-center text-muted py-3">暫無數據</td></tr>

                                        <tr class="table-warning border-top border-warning">
                                            <td colspan="3" class="fw-bold text-center text-dark py-2" style="font-size: 0.85rem;">以下為通膨重點監控數值補充</td>
                                        </tr>
                                        <tr>
                                            <td class="fw-bold text-secondary">美國 CPI (消費者物價指數 YoY)</td>
                                            <td class="text-center">
                                                <div class="fw-bold text-dark fs-6 font-monospace">{{ dashboardData.content.raw_indicators?.CPI ?? '--' }} %</div>
                                                <div class="text-muted mt-1 font-monospace" style="font-size: 0.75rem;">
                                                    (前值: {{ dashboardData.content.raw_indicators?.CPI_Prev ?? '--' }} %)
                                                </div>
                                            </td>
                                            <td class="text-center text-muted">-</td>
                                        </tr>
                                        <tr>
                                            <td class="fw-bold text-secondary">美國 PPI (生產者物價指數 YoY)</td>
                                            <td class="text-center">
                                                <div class="fw-bold text-dark fs-6 font-monospace">{{ dashboardData.content.raw_indicators?.PPI ?? '--' }} %</div>
                                                <div class="text-muted mt-1 font-monospace" style="font-size: 0.75rem;">
                                                    (前值: {{ dashboardData.content.raw_indicators?.PPI_Prev ?? '--' }} %)
                                                </div>
                                            </td>
                                            <td class="text-center text-muted">-</td>
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
    <div v-else class="text-center mt-5">
        <div class="spinner-border text-primary" role="status" v-if="isLoading"></div>
        <p class="mt-2 text-muted fw-bold" v-if="isLoading">載入戰情數據中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const rawResponseData = ref(null);
const isLoading = ref(true);
const dashboardData = computed(() => rawResponseData.value);
const dataSourceDisplay = computed(() => {
    if (!dashboardData.value) return '無數據';
    return `${dashboardData.value.source_type || '未知'} (時間: ${dashboardData.value.content?.update_time || '--'})`;
});

// =====================================
// 🔥 歷史紀錄切換邏輯
// =====================================
const historyList = ref([]);
const selectedHistory = ref('latest');

onMounted(async () => {
    await fetchDashboardData('latest');
    await fetchHistoryList();
});

const fetchHistoryList = async () => {
    try {
        const res = await $fetch('/api/macrowave/history-list').catch(() => null);
        if (res && res.success && Array.isArray(res.data)) {
            historyList.value = res.data;
        }
    } catch (e) {
        console.warn('目前尚無歷史清單 API 支援。');
    }
};

const fetchDashboardData = async (fileId) => {
    isLoading.value = true;
    try {
        let url = '/api/macrowave/latest';
        if (fileId !== 'latest') {
            url = `/api/macrowave/history?file=${fileId}`; 
        }
        
        const res = await $fetch(url);
        if (res && res.data) {
            rawResponseData.value = res.data;
        }
    } catch (e) {
        console.error('資料載入失敗', e);
    } finally { 
        isLoading.value = false; 
    }
};

const onHistoryChange = () => {
    fetchDashboardData(selectedHistory.value);
};

// =====================================
// Render 同步服務選項與同步邏輯
// =====================================
const runtimeConfig = useRuntimeConfig();
const renderUrls = String(runtimeConfig.public.macrowaveSyncApiUrls || '')
    .split(',')
    .map(url => url.trim().replace(/\/$/, ''))
    .filter(Boolean);
const syncServices = [
    { label: '自動選擇 Render 服務', value: 'auto' },
    ...renderUrls.map((url, index) => ({ label: `Render 服務 ${index + 1}`, value: url }))
];

const selectedSyncService = ref('auto');
const syncStatusText = ref('🔄 啟動雲端爬蟲');
const isSyncing = ref(false);

const triggerSync = async () => {
    if (!confirm('確定啟動雲端爬蟲？')) return;
    if (renderUrls.length === 0) {
        alert('尚未設定 MacroWave Render 同步服務網址。');
        return;
    }
    isSyncing.value = true;

    let urlsToTry = [];
    if (selectedSyncService.value === 'auto') {
        const allUrls = syncServices.filter(a => a.value !== 'auto').map(a => a.value);
        urlsToTry = [...allUrls].sort(() => 0.5 - Math.random());
    } else {
        urlsToTry = [selectedSyncService.value];
    }

    let success = false;
    for (let url of urlsToTry) {
        const accName = syncServices.find(a => a.value === url)?.label || 'Render 伺服器';
        syncStatusText.value = `嘗試中: ${accName}...`;
        
        try {
            await $fetch(`${url}/api/trigger-sync`, { method: 'POST', timeout: 15000 });
            alert(`✅ 指令已成功發送至 ${accName}！約 3 分鐘後將自動更新頁面。`);
            setTimeout(() => window.location.reload(), 180000);
            success = true;
            break;
        } catch (e) {
            console.warn(`[${accName}] 無回應或逾時`);
        }
    }

    if (!success) {
        alert('❌ 所選的 Render 服務皆無回應，請稍後再試。');
    }

    isSyncing.value = false;
    syncStatusText.value = '🔄 啟動雲端爬蟲';
};

// =====================================
// 獨立更新與上傳功能
// =====================================
const isSyncingTwstock = ref(false);
const triggerTwstockSync = async () => {
    isSyncingTwstock.value = true;
    try {
        const serviceUrl = String(runtimeConfig.public.macrowaveTwstockSyncApiUrl || '').replace(/\/$/, '');
        if (!serviceUrl) throw new Error('尚未設定台股 Render 同步服務網址');
        await $fetch(`${serviceUrl}/api/trigger-twstock-sync`, { method: 'POST' });
        alert('指令發送成功。');
        setTimeout(() => isSyncingTwstock.value = false, 150000);
    } catch (e) {
        alert(e?.message || '台股同步服務無回應。');
        isSyncingTwstock.value = false;
    }
};

const selectedFile = ref(null);
const isUploading = ref(false);
const handleFileSelect = (e) => selectedFile.value = e.target.files[0];
const uploadToServer = async () => {
    if (!selectedFile.value) return;
    isUploading.value = true;
    const reader = new FileReader();
    reader.onload = async (e) => {
        try {
            await $fetch('/api/macrowave/upload', { method: 'POST', headers: { 'X-Api-Key': 'macrowave168' }, body: JSON.parse(e.target.result) });
            alert('上傳成功'); window.location.reload();
        } finally { isUploading.value = false; }
    };
    reader.readAsText(selectedFile.value);
};
</script>

<style scoped>
.advice-Safe { background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; }
.advice-Caution { background-color: #fff3cd; color: #664d03; border: 1px solid #ffecb5; }
.advice-Flee { background-color: #f8d7da; color: #842029; border: 1px solid #f5c2c7; }
.metric-item { padding: 16px; border-radius: 10px; background-color: #f8f9fa; border: 1px solid #e9ecef; height: 100%; display: flex; flex-direction: column; justify-content: center; }
.metric-label { font-size: 0.85rem; color: #6c757d; margin-bottom: 6px; text-transform: uppercase; font-weight: bold;}
.metric-value { font-size: 1.25rem; font-weight: 700; color: #212529; }
.section-bar-tw { border-left: 5px solid #0d6efd; }
.section-bar-us { border-left: 5px solid #dc3545; }
.section-bar-cycle { border-left: 5px solid #198754; }
.section-bar-sentiment { border-left: 5px solid #ffc107; }
.cursor-pointer { cursor: pointer; }
</style>
