<template>
  <div class="stock-dashboard">
    <div class="header">
      <h2 class="title">美股 K 線圖與漲跌紀錄</h2>
      <div class="controls">
        <input 
          v-model="ticker" 
          type="text" 
          placeholder="輸入美股代號 (例: AAPL)" 
          class="ticker-input"
          @keyup.enter="fetchData"
        />
        
        <div class="toggle-switch timeframe-switch">
          <div class="slider" :class="timeframe"></div>
          <span :class="{ 'active': timeframe === 'daily' }" @click="timeframe = 'daily'">日 K</span>
          <span :class="{ 'active': timeframe === 'weekly' }" @click="timeframe = 'weekly'">週 K</span>
          <span :class="{ 'active': timeframe === 'monthly' }" @click="timeframe = 'monthly'">月 K</span>
        </div>

        <div class="toggle-switch" @click="toggleAdjusted">
          <div class="slider" :class="{ 'adjusted': isAdjusted }"></div>
          <span :class="{ 'active': !isAdjusted }">非還權</span>
          <span :class="{ 'active': isAdjusted }">還權息</span>
        </div>

        <div class="range-buttons">
          <button 
            v-for="r in ranges" 
            :key="r.value"
            :class="{ active: range === r.value }"
            @click="setRange(r.value)"
          >
            {{ r.label }}
          </button>
        </div>
        <button class="search-btn" @click="fetchData" :disabled="loading">
          {{ loading ? '載入中...' : '查詢' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 四宮格統計數據 -->
    <div class="stats-container" v-if="stats && !loading && !error">
      <div class="stat-box rise">
        <div class="stat-label">區間單{{ timeConfig.label }}最大漲幅</div>
        <div class="stat-value">+{{ stats.maxRise.toFixed(2) }}%</div>
        <div class="stat-date">{{ stats.maxRiseDate }} ( +{{ stats.maxRisePoint.toFixed(2) }} 點 )</div>
      </div>
      <div class="stat-box rise">
        <div class="stat-label">平均單{{ timeConfig.label }}上漲幅度</div>
        <div class="stat-value">+{{ stats.avgRise.toFixed(2) }}%</div>
        <div class="stat-date">發生次數: {{ stats.countRise }} 次</div>
      </div>
      <div class="stat-box fall">
        <div class="stat-label">區間單{{ timeConfig.label }}最大跌幅</div>
        <div class="stat-value">{{ stats.maxFall.toFixed(2) }}%</div>
        <div class="stat-date">{{ stats.maxFallDate }} ( {{ stats.maxFallPoint.toFixed(2) }} 點 )</div>
      </div>
      <div class="stat-box fall">
        <div class="stat-label">平均單{{ timeConfig.label }}下跌幅度</div>
        <div class="stat-value">{{ stats.avgFall.toFixed(2) }}%</div>
        <div class="stat-date">發生次數: {{ stats.countFall }} 次</div>
      </div>
    </div>

    <!-- 漲跌幅分佈統計塊 -->
    <div class="distribution-wrapper" v-if="stats && !loading && !error">
      <div class="dist-card rise-dist">
        <div class="dist-header">🚀 單{{ timeConfig.label }}漲幅超過 (發生次數)</div>
        <div class="dist-body">
          <div class="dist-item" v-for="i in 6" :key="'r'+i">
            <span class="dist-label">> {{ i }}%</span>
            <span class="dist-value text-success">{{ stats.distribution.rise[i] }}</span>
          </div>
        </div>
      </div>
      <div class="dist-card fall-dist">
        <div class="dist-header">⚠️ 單{{ timeConfig.label }}跌幅超過 (發生次數)</div>
        <div class="dist-body">
          <div class="dist-item" v-for="i in 6" :key="'f'+i">
            <span class="dist-label">< -{{ i }}%</span>
            <span class="dist-value text-danger">{{ stats.distribution.fall[i] }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-wrapper mb-4">
      <div id="us-stock-chart" ref="chartContainer" class="chart-container"></div>
    </div>

    <!-- 波段目標觸及機率 (一般漲跌幅) -->
    <div class="prob-wrapper" v-if="probStats && !loading && !error">
      <h3 class="prob-title">🎯 大盤波段目標觸及機率 (基於目前查詢區間)</h3>
      <div class="prob-explanation">
        <h5 class="fw-bold text-info mb-2">💡 我該如何解讀這張表？</h5>
        <p class="mb-2">以歷史每{{ timeConfig.label }}收盤價為基準，計算未來特定 K 棒數量內碰到指定漲跌幅的機率。包含極短線(1%, 3%)與波段目標。</p>
      </div>
      
      <div class="prob-tables mt-3">
        <!-- 上漲機率表 -->
        <div class="prob-card">
          <div class="prob-header text-success">📈 多方目標 (上漲)</div>
          <div class="table-responsive">
            <table class="prob-table">
              <thead>
                <tr>
                  <th>目標幅度</th>
                  <th v-for="hLabel in timeConfig.horizonLabels" :key="'th_rise_'+hLabel">{{ hLabel }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in probStats.thresholds" :key="'rise_'+t">
                  <td class="fw-bold text-success">+{{ t }}%</td>
                  <td v-for="(val, idx) in probStats.results.rise[t]" :key="'val_rise_'+t+'_'+idx">{{ val }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 下跌機率表 -->
        <div class="prob-card">
          <div class="prob-header text-danger">📉 空方目標 (下跌)</div>
          <div class="table-responsive">
            <table class="prob-table">
              <thead>
                <tr>
                  <th>目標幅度</th>
                  <th v-for="hLabel in timeConfig.horizonLabels" :key="'th_fall_'+hLabel">{{ hLabel }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in probStats.thresholds" :key="'fall_'+t">
                  <td class="fw-bold text-danger">-{{ t }}%</td>
                  <td v-for="(val, idx) in probStats.results.fall[t]" :key="'val_fall_'+t+'_'+idx">{{ val }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 選擇權履約價回測矩陣 -->
    <div class="opt-prob-wrapper" v-if="processedData.kLineValues.length > 0 && !loading && !error">
      <h3 class="prob-title text-warning border-bottom border-secondary pb-2 mb-3">🦅 選擇權履約價風險回測矩陣</h3>
      
      <!-- 🔥 新增：詳細解說面板 -->
      <div class="opt-explanation mb-4">
        <h5 class="fw-bold text-warning mb-2">💡 兩張表的關係與機率計算邏輯</h5>
        <ul class="mb-0 ps-3">
          <li class="mb-2"><strong>兩表關聯：</strong>上半部「大盤波段目標」是股票的<b>基礎體質慣性</b>（固定幅度）。本區塊則是<b>專屬實戰風險</b>，系統會自動換算您輸入的履約價與「最新參考價」相距幾 %，再用該 % 數去調用與上方完全相同的演算法，得出更貼近真實操作的風險機率。</li>
          <li class="mb-2"><strong>滾動回測 (Rolling Backtest)：</strong>機率並非只看頭尾。系統會把所選歷史區間內的<b>「每一個交易日」都當作進場點</b>，並往未來 N 週內展開一個「滑動窗口」進行地毯式掃描。</li>
          <li><strong>嚴格的觸及判定：</strong>作為選擇權賣方最怕盤中被洗出場。因此系統的判定標準是<b>「盤中最高價 / 最低價」</b>而非收盤價。只要在觀察窗口內，極端價格曾被「插針」掃到（漲破 Call 或 跌破 Put），就會被無情地記上一筆敗績。機率 ＝ <code>(觸及總次數 ÷ 總測試窗口數)</code>。</li>
        </ul>
      </div>

      <div class="opt-form-card mb-4">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-3">
          <h5 class="m-0 text-white">設定評估部位</h5>
          <div class="d-flex flex-wrap gap-3 align-items-center">
            <div class="latest-price-badge">
              <span class="badge-label">區間最高價:</span> <span class="fw-bold text-success">${{ periodExtremes.high.toFixed(2) }}</span>
            </div>
            <div class="latest-price-badge">
              <span class="badge-label">區間最低價:</span> <span class="fw-bold text-danger">${{ periodExtremes.low.toFixed(2) }}</span>
            </div>
            <div class="latest-price-badge highlight-badge">
              <span class="badge-label">最新參考價:</span> <span class="fw-bold text-warning fs-5">${{ latestClosePrice.toFixed(2) }}</span>
            </div>
          </div>
        </div>
        
        <div class="form-group mb-3">
          <label>策略類型</label>
          <select v-model="optStrategy" class="dark-input w-auto">
            <option value="bullPut">📉 賣權多頭 (Bull Put Spread)</option>
            <option value="bearCall">📈 買權空頭 (Bear Call Spread)</option>
            <option value="ironCondor">🦅 鐵鷹 (Iron Condor)</option>
          </select>
        </div>

        <div class="strikes-grid">
          <div class="form-group" v-if="optStrategy === 'bullPut' || optStrategy === 'ironCondor'">
            <label class="text-danger">賣出 Put 履約價 (下方防線)</label>
            <input type="number" step="0.5" v-model.number="optStrikes.shortPut" class="dark-input" placeholder="輸入履約價" />
            <span class="fs-7 text-muted mt-1" v-if="optStrikes.shortPut && latestClosePrice">
              距現價距離: <span class="text-warning">{{ (((optStrikes.shortPut - latestClosePrice) / latestClosePrice) * 100).toFixed(2) }}%</span>
            </span>
          </div>

          <div class="form-group" v-if="optStrategy === 'bearCall' || optStrategy === 'ironCondor'">
            <label class="text-danger">賣出 Call 履約價 (上方防線)</label>
            <input type="number" step="0.5" v-model.number="optStrikes.shortCall" class="dark-input" placeholder="輸入履約價" />
            <span class="fs-7 text-muted mt-1" v-if="optStrikes.shortCall && latestClosePrice">
              距現價距離: <span class="text-warning">+{{ (((optStrikes.shortCall - latestClosePrice) / latestClosePrice) * 100).toFixed(2) }}%</span>
            </span>
          </div>
        </div>
      </div>

      <div class="prob-tables mt-3" v-if="optProbResults && optProbResults.results.length > 0">
        <!-- Put 端風險表 -->
        <div class="prob-card" v-if="optStrategy === 'bullPut' || optStrategy === 'ironCondor'">
          <div class="prob-header text-danger">⚠️ 跌破 Short Put (${{ optStrikes.shortPut || '未輸入' }}) 的機率</div>
          <div class="table-responsive">
            <table class="prob-table">
              <thead>
                <tr>
                  <th>歷史資料區間</th>
                  <th v-for="hLabel in timeConfig.horizonLabels.slice(0,3)" :key="'opt_th_put_'+hLabel">{{ hLabel }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="res in optProbResults.results" :key="'put_'+res.label">
                  <td class="fw-bold text-white">{{ res.label }}</td>
                  <td v-if="!res.isValid" colspan="3" class="text-muted text-center">資料量不足 (請切換更長年份)</td>
                  <template v-else>
                    <td :class="{'text-danger fw-bold': res.putProbs[0] > 10}">{{ res.putProbs[0] }}%</td>
                    <td :class="{'text-danger fw-bold': res.putProbs[1] > 10}">{{ res.putProbs[1] }}%</td>
                    <td :class="{'text-danger fw-bold': res.putProbs[2] > 10}">{{ res.putProbs[2] }}%</td>
                  </template>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Call 端風險表 -->
        <div class="prob-card" v-if="optStrategy === 'bearCall' || optStrategy === 'ironCondor'">
          <div class="prob-header text-danger">⚠️ 突破 Short Call (${{ optStrikes.shortCall || '未輸入' }}) 的機率</div>
          <div class="table-responsive">
            <table class="prob-table">
              <thead>
                <tr>
                  <th>歷史資料區間</th>
                  <th v-for="hLabel in timeConfig.horizonLabels.slice(0,3)" :key="'opt_th_call_'+hLabel">{{ hLabel }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="res in optProbResults.results" :key="'call_'+res.label">
                  <td class="fw-bold text-white">{{ res.label }}</td>
                  <td v-if="!res.isValid" colspan="3" class="text-muted text-center">資料量不足 (請切換更長年份)</td>
                  <template v-else>
                    <td :class="{'text-danger fw-bold': res.callProbs[0] > 10}">{{ res.callProbs[0] }}%</td>
                    <td :class="{'text-danger fw-bold': res.callProbs[1] > 10}">{{ res.callProbs[1] }}%</td>
                    <td :class="{'text-danger fw-bold': res.callProbs[2] > 10}">{{ res.callProbs[2] }}%</td>
                  </template>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';

const ticker = ref('AAPL');
const range = ref('1y');
const ranges = [
  { label: '1 年', value: '1y' },
  { label: '2 年', value: '2y' },
  { label: '3 年', value: '3y' },
  { label: '5 年', value: '5y' }
];

const timeframe = ref('daily');

const loading = ref(false);
const error = ref('');
const rawData = ref([]); 
const isAdjusted = ref(false);

const stats = ref(null);
const probStats = ref(null); 
const optStrategy = ref('ironCondor');
const optStrikes = ref({ shortPut: null, shortCall: null });
const latestClosePrice = ref(0);
const optProbResults = ref(null);

const chartContainer = ref(null);
let chartInstance = null;
let resizeObserver = null;

const timeConfig = computed(() => {
  if (timeframe.value === 'daily') {
    return {
      label: '日', horizons: [5, 10, 15, 20, 25],
      horizonLabels: ['一週內 (5T)', '兩週內 (10T)', '三週內 (15T)', '四週內 (20T)', '五週內 (25T)'],
      historySpans: [
        { label: '過去 1 年', periods: 252 }, { label: '過去 2 年', periods: 504 },
        { label: '過去 3 年', periods: 756 }, { label: '過去 5 年', periods: 1260 }
      ]
    };
  } else if (timeframe.value === 'weekly') {
    return {
      label: '週', horizons: [1, 2, 3, 4, 5],
      horizonLabels: ['一週內 (1T)', '兩週內 (2T)', '三週內 (3T)', '四週內 (4T)', '五週內 (5T)'],
      historySpans: [
        { label: '過去 1 年', periods: 52 }, { label: '過去 2 年', periods: 104 },
        { label: '過去 3 年', periods: 156 }, { label: '過去 5 年', periods: 260 }
      ]
    };
  } else { 
    return {
      label: '月', horizons: [1, 2, 3, 4, 5],
      horizonLabels: ['一個月內 (1T)', '兩個月內 (2T)', '三個月內 (3T)', '四個月內 (4T)', '五個月內 (5T)'],
      historySpans: [
        { label: '過去 1 年', periods: 12 }, { label: '過去 2 年', periods: 24 },
        { label: '過去 3 年', periods: 36 }, { label: '過去 5 年', periods: 60 }
      ]
    };
  }
});

const extractVolume = (obj) => {
  for (const key in obj) {
    if (key.toLowerCase() === 'volume' || key.toLowerCase() === 'vol') {
      return obj[key];
    }
  }
  return 0;
};

const processedData = computed(() => {
  if (!rawData.value || rawData.value.length === 0) return { dates: [], kLineValues: [], volumes: [] };

  const getWeekKey = (dateStr) => {
    const d = new Date(dateStr);
    d.setDate(d.getDate() - d.getDay() + (d.getDay() === 0 ? -6 : 1));
    return d.toISOString().split('T')[0];
  };

  const grouped = {};
  rawData.value.forEach(item => {
    let groupKey = item.time;
    if (timeframe.value === 'weekly') groupKey = getWeekKey(item.time);
    if (timeframe.value === 'monthly') groupKey = item.time.substring(0, 7);

    const rawVol = extractVolume(item);
    const itemVol = Number(String(rawVol).replace(/,/g, '')) || 0;

    if (!grouped[groupKey]) {
      grouped[groupKey] = {
        time: item.time, open: item.open, high: item.high, low: item.low, close: item.close,
        volume: itemVol, adjclose: item.adjclose
      };
    } else {
      grouped[groupKey].time = item.time; 
      grouped[groupKey].high = Math.max(grouped[groupKey].high, item.high);
      grouped[groupKey].low = Math.min(grouped[groupKey].low, item.low);
      grouped[groupKey].close = item.close; 
      grouped[groupKey].volume += itemVol; 
      grouped[groupKey].adjclose = item.adjclose;
    }
  });

  const dates = [];
  const kLineValues = [];
  const volumes = [];

  Object.values(grouped).forEach(item => {
    dates.push(item.time);
    let o = item.open, c = item.close, l = item.low, h = item.high;
    if (isAdjusted.value && item.adjclose && item.close) {
      const ratio = item.adjclose / item.close;
      o *= ratio; c *= ratio; l *= ratio; h *= ratio;
    }
    kLineValues.push([o, c, l, h]);
    volumes.push(item.volume);
  });

  return { dates, kLineValues, volumes };
});

const periodExtremes = computed(() => {
  const kValues = processedData.value.kLineValues;
  if (!kValues || kValues.length === 0) return { high: 0, low: 0 };
  let high = -Infinity;
  let low = Infinity;
  kValues.forEach(k => {
    if (k[3] > high) high = k[3]; 
    if (k[2] < low) low = k[2];   
  });
  return { high, low };
});

const setRange = (newRange) => {
  range.value = newRange;
  fetchData();
};

const toggleAdjusted = () => {
  isAdjusted.value = !isAdjusted.value;
};

watch(processedData, (newVal) => {
  if (newVal.dates.length > 0) {
    renderChart(newVal.dates, newVal.kLineValues, newVal.volumes);
    calculateStats(newVal.dates, newVal.kLineValues);
    calculateProbabilities(newVal.kLineValues);
    latestClosePrice.value = newVal.kLineValues[newVal.kLineValues.length - 1][1];
    calculateOptionProbabilities(newVal.kLineValues);
  }
});

watch([optStrategy, optStrikes], () => {
  if (processedData.value.kLineValues.length > 0) {
    calculateOptionProbabilities(processedData.value.kLineValues);
  }
}, { deep: true });

const calculateStats = (dates, kLineValues) => {
  let maxRise = 0, maxFall = 0, maxRiseDate = '', maxFallDate = '';
  let maxRisePoint = 0, maxFallPoint = 0, sumRise = 0, countRise = 0, sumFall = 0, countFall = 0;

  let distribution = { rise: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0 }, fall: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0 } };

  for (let i = 1; i < kLineValues.length; i++) {
    const prevClose = kLineValues[i - 1][1], currClose = kLineValues[i][1];
    const changePercent = ((currClose - prevClose) / prevClose) * 100;
    const changePoint = currClose - prevClose;

    if (changePercent > 0) {
      sumRise += changePercent; countRise++;
      if (changePercent > maxRise) { maxRise = changePercent; maxRiseDate = dates[i]; maxRisePoint = changePoint; }
      if (changePercent >= 1) distribution.rise[1]++;
      if (changePercent >= 2) distribution.rise[2]++;
      if (changePercent >= 3) distribution.rise[3]++;
      if (changePercent >= 4) distribution.rise[4]++;
      if (changePercent >= 5) distribution.rise[5]++;
      if (changePercent >= 6) distribution.rise[6]++;
    } else if (changePercent < 0) {
      sumFall += changePercent; countFall++;
      if (changePercent < maxFall) { maxFall = changePercent; maxFallDate = dates[i]; maxFallPoint = changePoint; }
      if (changePercent <= -1) distribution.fall[1]++;
      if (changePercent <= -2) distribution.fall[2]++;
      if (changePercent <= -3) distribution.fall[3]++;
      if (changePercent <= -4) distribution.fall[4]++;
      if (changePercent <= -5) distribution.fall[5]++;
      if (changePercent <= -6) distribution.fall[6]++;
    }
  }

  const avgRise = countRise > 0 ? sumRise / countRise : 0;
  const avgFall = countFall > 0 ? sumFall / countFall : 0;
  stats.value = { maxRise, maxFall, maxRiseDate, maxFallDate, maxRisePoint, maxFallPoint, avgRise, avgFall, countRise, countFall, distribution };
};

const calculateProbabilities = (kLineValues) => {
  const horizons = timeConfig.value.horizons; 
  const thresholds = [1, 3, 5, 7, 10, 15, 20, 25, 30];

  let results = { rise: {}, fall: {} };
  thresholds.forEach(t => {
    results.rise[t] = [0, 0, 0, 0, 0];
    results.fall[t] = [0, 0, 0, 0, 0];
  });

  let totalCounts = [0, 0, 0, 0, 0];

  for (let i = 0; i < kLineValues.length; i++) {
    const currentClose = kLineValues[i][1]; 
    horizons.forEach((periods, hIndex) => {
      if (i + periods < kLineValues.length) {
        totalCounts[hIndex]++;
        let maxHigh = -Infinity, minLow = Infinity;
        for (let j = 1; j <= periods; j++) {
           if (kLineValues[i + j][3] > maxHigh) maxHigh = kLineValues[i + j][3];
           if (kLineValues[i + j][2] < minLow) minLow = kLineValues[i + j][2];
        }
        const maxRisePct = ((maxHigh - currentClose) / currentClose) * 100;
        const maxFallPct = ((minLow - currentClose) / currentClose) * 100;

        thresholds.forEach(t => {
          if (maxRisePct >= t) results.rise[t][hIndex]++;
          if (maxFallPct <= -t) results.fall[t][hIndex]++; 
        });
      }
    });
  }

  thresholds.forEach(t => {
    for (let hIndex = 0; hIndex < 5; hIndex++) {
       const total = totalCounts[hIndex];
       results.rise[t][hIndex] = total > 0 ? ((results.rise[t][hIndex] / total) * 100).toFixed(1) : 0;
       results.fall[t][hIndex] = total > 0 ? ((results.fall[t][hIndex] / total) * 100).toFixed(1) : 0;
    }
  });

  probStats.value = { results, thresholds, horizons, totalCounts };
};

const calculateOptionProbabilities = (kLineValues) => {
  const latestPrice = latestClosePrice.value;
  const { shortPut, shortCall } = optStrikes.value;
  
  const spPct = shortPut ? ((shortPut - latestPrice) / latestPrice) * 100 : null; 
  const scPct = shortCall ? ((shortCall - latestPrice) / latestPrice) * 100 : null; 

  const horizons = timeConfig.value.horizons.slice(0, 3); 
  const historySpans = timeConfig.value.historySpans;

  let results = [];

  historySpans.forEach(span => {
    const sliceData = kLineValues.slice(Math.max(0, kLineValues.length - span.periods));
    const isValid = sliceData.length >= (span.periods * 0.8);

    if (!isValid) {
      results.push({ label: span.label, isValid: false });
      return;
    }

    let totalCounts = [0, 0, 0];
    let hitPut = [0, 0, 0];
    let hitCall = [0, 0, 0];

    for (let i = 0; i < sliceData.length; i++) {
      const currentClose = sliceData[i][1];
      
      horizons.forEach((periods, hIndex) => {
        if (i + periods < sliceData.length) {
          totalCounts[hIndex]++;
          let minLow = Infinity, maxHigh = -Infinity;
          for (let j = 1; j <= periods; j++) {
            if (sliceData[i+j][2] < minLow) minLow = sliceData[i+j][2];
            if (sliceData[i+j][3] > maxHigh) maxHigh = sliceData[i+j][3];
          }
          const dropPct = ((minLow - currentClose) / currentClose) * 100;
          const risePct = ((maxHigh - currentClose) / currentClose) * 100;

          if (spPct !== null && dropPct <= spPct) hitPut[hIndex]++;
          if (scPct !== null && risePct >= scPct) hitCall[hIndex]++;
        }
      });
    }

    results.push({
      label: span.label,
      isValid: true,
      putProbs: totalCounts.map((tot, idx) => tot > 0 ? ((hitPut[idx]/tot)*100).toFixed(1) : 0),
      callProbs: totalCounts.map((tot, idx) => tot > 0 ? ((hitCall[idx]/tot)*100).toFixed(1) : 0)
    });
  });

  optProbResults.value = { results };
};

const renderChart = (dates, kLineValues, volumes) => {
  const dom = chartContainer.value;
  if (!dom) return;

  if (chartInstance) chartInstance.dispose();
  chartInstance = echarts.init(dom);

  const existingDatesSet = new Set(dates); 
  const markLineData = [];

  const fedMeetingDates = [
    '2023-02-01', '2023-03-22', '2023-05-03', '2023-06-14', '2023-07-26', '2023-09-20', '2023-11-01', '2023-12-13',
    '2024-01-31', '2024-03-20', '2024-05-01', '2024-06-12', '2024-07-31', '2024-09-18', '2024-11-07', '2024-12-18',
    '2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18', '2025-07-30', '2025-09-17', '2025-10-29', '2025-12-10',
    '2026-01-28', '2026-03-18', '2026-05-06', '2026-06-17', '2026-07-29', '2026-09-16', '2026-11-04', '2026-12-16'
  ];

  fedMeetingDates.forEach(d => {
    if (existingDatesSet.has(d)) {
      markLineData.push({
        xAxis: d,
        lineStyle: { color: '#8c8f98', type: 'dashed', opacity: 0.5 },
        label: { formatter: 'Fed', position: 'insideStartBottom', color: '#8c8f98' }
      });
    }
  });

  const option = {
    backgroundColor: 'transparent',
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'cross', link: [{ xAxisIndex: 'all' }] },
      formatter: function (params) {
        const dataIdx = params[0].dataIndex;
        const kData = kLineValues[dataIdx];
        const vData = volumes[dataIdx]; 
        
        let res = `<div style="font-weight:bold;margin-bottom:8px;border-bottom:1px solid #434651;padding-bottom:5px;color:#fff;">${dates[dataIdx]}</div>`;
        
        if (kData) {
          const isUp = kData[1] >= kData[0];
          const color = isUp ? '#26a69a' : '#ef5350';
          res += `<div style="display:flex;justify-content:space-between;gap:24px;margin-bottom:4px;"><span>開盤:</span> <span style="font-weight:bold;color:#d1d4dc;">${Number(kData[0]).toFixed(2)}</span></div>`;
          res += `<div style="display:flex;justify-content:space-between;gap:24px;margin-bottom:4px;"><span>收盤:</span> <span style="font-weight:bold;color:${color};">${Number(kData[1]).toFixed(2)}</span></div>`;
          res += `<div style="display:flex;justify-content:space-between;gap:24px;margin-bottom:4px;"><span>最低:</span> <span style="font-weight:bold;color:#d1d4dc;">${Number(kData[2]).toFixed(2)}</span></div>`;
          res += `<div style="display:flex;justify-content:space-between;gap:24px;"><span>最高:</span> <span style="font-weight:bold;color:#d1d4dc;">${Number(kData[3]).toFixed(2)}</span></div>`;
        }
        if (vData !== undefined) {
          const volStr = vData > 0 ? Number(vData).toLocaleString() : '無資料 / 0';
          res += `<div style="display:flex;justify-content:space-between;gap:24px;margin-top:8px;border-top:1px solid #434651;padding-top:8px;"><span>成交量:</span> <span style="font-weight:bold;color:#e0ac00;">${volStr}</span></div>`;
        }
        
        return res;
      }
    },
    axisPointer: { link: [{ xAxisIndex: 'all' }] },
    grid: [
      { left: '5%', right: '5%', top: '5%', height: '60%' }, 
      { left: '5%', right: '5%', top: '70%', height: '20%' }  
    ],
    xAxis: [
      { type: 'category', data: dates, boundaryGap: false, axisLine: { lineStyle: { color: '#434651' } }, splitLine: { show: false }, axisLabel: { show: false } },
      { type: 'category', gridIndex: 1, data: dates, boundaryGap: false, axisLine: { lineStyle: { color: '#434651' } }, axisLabel: { color: '#8c8f98' } }
    ],
    yAxis: [
      { scale: true, position: 'right', axisLine: { lineStyle: { color: '#434651' } }, axisLabel: { color: '#8c8f98' }, splitLine: { lineStyle: { color: '#2B2B43' } } },
      { type: 'value', gridIndex: 1, position: 'right', splitLine: { show: false }, axisLabel: { show: false }, min: 0 } 
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
      { show: true, type: 'slider', xAxisIndex: [0, 1], top: '92%', bottom: '1%', borderColor: '#2B2B43', textStyle: { color: '#8c8f98' } }
    ],
    series: [
      {
        name: isAdjusted.value ? 'K 線 (還權息)' : 'K 線',
        type: 'candlestick',
        data: kLineValues,
        itemStyle: { color: '#26a69a', color0: '#ef5350', borderColor: '#26a69a', borderColor0: '#ef5350' },
        markLine: { symbol: ['none', 'none'], data: markLineData }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes.map((vol, idx) => ({
          value: vol,
          itemStyle: { color: kLineValues[idx][1] >= kLineValues[idx][0] ? '#26a69a' : '#ef5350' }
        }))
      }
    ]
  };

  chartInstance.setOption(option);

  if (!resizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      if (chartInstance) chartInstance.resize();
    });
    resizeObserver.observe(dom);
  }
};

const fetchData = async () => {
  if (!ticker.value) { error.value = '請輸入股票代號'; return; }
  loading.value = true; error.value = '';
  
  try {
    const response = await fetch(`/api/macrowave/stock?ticker=${ticker.value.toUpperCase()}&range=${range.value}`);
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.statusMessage || errData.message || '取得資料失敗');
    }
    const data = await response.json();
    if (data.error) throw new Error(data.message);
    if (!data || data.length === 0) throw new Error('找不到該股票資料');

    rawData.value = data; 
  } catch (err) {
    error.value = err.message; console.error(err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => { /* fetchData(); */ });

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect();
  if (chartInstance) { chartInstance.dispose(); chartInstance = null; }
});
</script>

<style scoped>
.stock-dashboard {
  background-color: #131722; color: #d1d4dc; padding: 24px;
  border-radius: 12px; font-family: -apple-system, sans-serif;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); margin: 0 auto;
}

.header { display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; }
@media (min-width: 768px) { .header { flex-direction: row; justify-content: space-between; align-items: center; } }
.title { margin: 0; font-size: 1.5rem; font-weight: 600; color: #fff; }
.controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }

.ticker-input {
  background-color: #2a2e39; border: 1px solid #434651; color: #fff;
  padding: 10px 16px; border-radius: 6px; font-size: 14px; outline: none; width: 150px;
}
.ticker-input:focus { border-color: #2962ff; }

/* 開關樣式共用 */
.toggle-switch {
  display: flex; background-color: #2a2e39; border-radius: 6px;
  position: relative; cursor: pointer; padding: 4px; user-select: none; align-items: center;
}
.toggle-switch span { width: 70px; text-align: center; padding: 6px 0; font-size: 14px; color: #8c8f98; z-index: 1; transition: color 0.3s; }
.toggle-switch span.active { color: #fff; font-weight: bold; }
.toggle-switch .slider {
  position: absolute; top: 4px; bottom: 4px; left: 4px; width: calc(50% - 4px);
  background-color: #2962ff; border-radius: 4px; transition: transform 0.3s ease;
}
.toggle-switch .slider.adjusted { transform: translateX(100%); }

.timeframe-switch span { width: 55px; }
.timeframe-switch .slider { width: calc(33.33% - 4px); }
.timeframe-switch .slider.daily { transform: translateX(0%); }
.timeframe-switch .slider.weekly { transform: translateX(100%); }
.timeframe-switch .slider.monthly { transform: translateX(200%); }

.range-buttons { display: flex; background-color: #2a2e39; border-radius: 6px; overflow: hidden; }
.range-buttons button { background: none; border: none; color: #b2b5be; padding: 10px 16px; font-size: 14px; cursor: pointer; }
.range-buttons button:hover { background-color: #363a45; color: #fff; }
.range-buttons button.active { background-color: #2962ff; color: #fff; font-weight: 500; }

.search-btn { background-color: #2962ff; color: #fff; border: none; padding: 10px 24px; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; }
.search-btn:hover { background-color: #1e4bd8; }

.stats-container { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px; }
@media (max-width: 992px) { .stats-container { grid-template-columns: repeat(2, 1fr); } }

.stat-box { background-color: #1e222d; border: 1px solid #2b2b43; border-radius: 8px; padding: 16px; text-align: center; transition: transform 0.2s; }
.stat-box:hover { transform: translateY(-2px); }
.stat-box.rise { border-left: 4px solid #26a69a; }
.stat-box.fall { border-left: 4px solid #ef5350; }
.stat-label { color: #8c8f98; font-size: 0.9rem; margin-bottom: 8px; }
.stat-value { font-size: 1.8rem; font-weight: 700; margin-bottom: 4px; }
.stat-date { color: #b2b5be; font-size: 0.85rem; }

.distribution-wrapper { display: flex; gap: 16px; margin-bottom: 16px; }
@media (max-width: 992px) { .distribution-wrapper { flex-direction: column; } }
.dist-card { flex: 1; background-color: #1e222d; border: 1px solid #2b2b43; border-radius: 8px; padding: 16px; }
.dist-card.rise-dist { border-top: 3px solid #26a69a; }
.dist-card.fall-dist { border-top: 3px solid #ef5350; }
.dist-header { font-weight: 600; margin-bottom: 12px; font-size: 1rem; color: #d1d4dc; }
.dist-body { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.dist-item { display: flex; flex-direction: column; align-items: center; background-color: #2a2e39; padding: 10px; border-radius: 6px; flex: 1; min-width: 50px; }
.dist-label { font-size: 0.85rem; color: #8c8f98; margin-bottom: 4px; }
.dist-value { font-size: 1.2rem; font-weight: 700; }
.text-success { color: #26a69a; }
.text-danger { color: #ef5350; }

.prob-wrapper { background-color: #1e222d; border: 1px solid #2b2b43; border-radius: 8px; padding: 20px; margin-bottom: 24px; }
.prob-title { margin-top: 0; margin-bottom: 12px; font-size: 1.2rem; color: #fff; }
.prob-explanation { background-color: rgba(38, 166, 154, 0.05); border-left: 4px solid #26a69a; padding: 16px; border-radius: 0 6px 6px 0; margin-bottom: 20px; color: #d1d4dc; font-size: 0.95rem; line-height: 1.5; }
.highlight-text { background-color: #2a2e39; padding: 12px; border-radius: 6px; margin-top: 8px; border: 1px solid #434651; }
.prob-tables { display: flex; gap: 16px; }
@media (max-width: 992px) { .prob-tables { flex-direction: column; } }
.prob-card { flex: 1; background-color: #2a2e39; border-radius: 6px; overflow-x: auto; }
.prob-header { padding: 12px 16px; font-weight: bold; background-color: rgba(0,0,0,0.2); }
.table-responsive { overflow-x: auto; }
.prob-table { width: 100%; border-collapse: collapse; text-align: right; white-space: nowrap; }
.prob-table th, .prob-table td { padding: 10px 16px; border-bottom: 1px solid #1e222d; }
.prob-table th { color: #8c8f98; font-weight: 500; text-align: right; }
.prob-table tbody tr:hover { background-color: rgba(255,255,255,0.02); }

/* 🔥 選擇權回測模組與解說樣式 */
.opt-prob-wrapper { background-color: #1e222d; border: 1px solid #2b2b43; border-radius: 8px; padding: 20px; margin-bottom: 24px; }
.opt-explanation { background-color: rgba(224, 172, 0, 0.05); border-left: 4px solid #e0ac00; padding: 16px; border-radius: 0 6px 6px 0; color: #d1d4dc; font-size: 0.95rem; line-height: 1.6; }
.opt-form-card { background-color: #2a2e39; padding: 20px; border-radius: 8px; border: 1px solid #434651; }
.latest-price-badge { background-color: #1e222d; padding: 10px 16px; border-radius: 6px; border: 1px solid #434651; display: flex; align-items: center; gap: 8px; }
.latest-price-badge.highlight-badge { border-color: #e0ac00 !important; background-color: rgba(224, 172, 0, 0.1); }
.badge-label { color: #d1d4dc; font-size: 0.85rem; }

.form-group { margin-bottom: 14px; display: flex; flex-direction: column; gap: 4px; }
.form-group label { font-size: 0.85rem; color: #8c8f98; }
.dark-input { background-color: #131722; border: 1px solid #434651; color: #fff; padding: 10px; border-radius: 6px; outline: none; }
.dark-input:focus { border-color: #2962ff; }
.strikes-grid { display: flex; gap: 16px; flex-wrap: wrap; }
.strikes-grid .form-group { flex: 1; min-width: 200px; }
.fs-7 { font-size: 0.85rem; }

.error-message { background-color: rgba(239, 83, 80, 0.1); color: #ef5350; padding: 12px 16px; border-radius: 6px; margin-bottom: 24px; border: 1px solid rgba(239, 83, 80, 0.2); }
.chart-wrapper { position: relative; width: 100%; height: 650px; border: 1px solid #2b2b43; border-radius: 8px; overflow: hidden; background-color: #1E222D; }
.chart-container { width: 100%; height: 100%; }
</style>
