<template>
  <div class="container pb-5 mt-4">
    
    <div class="card shadow-sm border-0 mb-4 bg-light">
      <div class="card-body">
        <h5 class="fw-bold text-success mb-3">⏳ 台股歷史週 KD 轉折大數據回測</h5>
        <p class="text-muted small mb-3">
          本系統自動掃描歷史至目前的每一次真實週 KD 交叉。當發生轉折時，結算前一波的<strong>「漲跌空間」</strong>與<strong>「交易天數」</strong>，並自動對比當前年代的<strong>「平均動態極值」</strong>。您可展開每一年份，並自由切換「週 K 線 (看大趨勢)」或「日 K 線 (看均線防守)」。<br>
          <span class="text-danger">※ 註：歷史數據起點依 Yahoo API 實際提供年份為準 (台股約從 1997 年起算)。</span>
        </p>
        
        <div class="d-flex flex-wrap gap-2">
            <button v-for="decade in availableDecades" :key="decade.id" 
                    @click="activeDecade = decade.id"
                    :class="['btn fw-bold px-4', activeDecade === decade.id ? 'btn-success' : 'btn-outline-success']">
                {{ decade.label }}
            </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="text-center my-5">
      <div class="spinner-border text-success"></div><p class="mt-2 fw-bold text-success">歷史大數據解析、交易日與動態極值精算中...</p>
    </div>

    <div v-if="errorMsg" class="alert alert-danger fw-bold text-center">
      ❌ 錯誤：{{ errorMsg }}
    </div>

    <div v-if="!isLoading && groupedData[activeDecade]">
      
      <div class="row mb-4 g-2">
        <div class="col-md-3">
            <div class="card border-success h-100 shadow-sm text-center p-2">
                <h6 class="text-muted fw-bold mb-1 small">年均交叉次數</h6>
                <div class="fs-4 fw-bold text-success">{{ getDecadeAvgCrosses(activeDecade) }} <span class="fs-6">次</span></div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card border-danger h-100 shadow-sm text-center p-2">
                <h6 class="text-muted fw-bold mb-1 small">年代動態極值 (均漲)</h6>
                <div class="fs-4 fw-bold text-danger">+{{ activeAvgUp.toFixed(0) }} <span class="fs-6">點</span></div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card border-primary h-100 shadow-sm text-center p-2">
                <h6 class="text-muted fw-bold mb-1 small">年代動態極值 (均跌)</h6>
                <div class="fs-4 fw-bold text-primary">-{{ activeAvgDown.toFixed(0) }} <span class="fs-6">點</span></div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card border-dark h-100 shadow-sm text-center p-2">
                <h6 class="text-muted fw-bold mb-1 small">最大波段 (漲 / 跌)</h6>
                <div class="fs-5 fw-bold text-dark mt-1">
                    <span class="text-danger">+{{ getDecadeBestWave(activeDecade) }}</span> / 
                    <span class="text-success">{{ getDecadeWorstWave(activeDecade) }}</span>
                </div>
            </div>
        </div>
      </div>

      <div class="accordion shadow-sm" id="historyAccordion">
        <div class="accordion-item" v-for="yearData in groupedData[activeDecade]" :key="yearData.year">
          <h2 class="accordion-header" :id="'heading' + yearData.year">
            <button class="accordion-button collapsed fw-bold fs-5 d-flex justify-content-between align-items-center" type="button" data-bs-toggle="collapse" :data-bs-target="'#collapse' + yearData.year">
              <span>📅 {{ yearData.year }} 年</span>
              <span class="badge ms-3 me-3" :class="yearData.crosses.length >= 6 && yearData.crosses.length <= 8 ? 'bg-success' : 'bg-warning text-dark'">
                  全年交叉: {{ yearData.crosses.length }} 次
              </span>
            </button>
          </h2>
          <div :id="'collapse' + yearData.year" class="accordion-collapse collapse" data-bs-parent="#historyAccordion">
            <div class="accordion-body bg-light p-3">
                
                <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                    <h6 class="fw-bold text-dark mb-0">📌 本年度轉折明細</h6>
                    <div class="d-flex align-items-center gap-2">
                        <div class="btn-group shadow-sm" v-if="activeChartYear === yearData.year">
                            <button :class="['btn btn-sm fw-bold', chartPeriodType === 'daily' ? 'btn-primary' : 'btn-outline-primary']" @click="changeChartPeriod('daily', yearData.year)">日 K 線 (含均線)</button>
                            <button :class="['btn btn-sm fw-bold', chartPeriodType === 'weekly' ? 'btn-primary' : 'btn-outline-primary']" @click="changeChartPeriod('weekly', yearData.year)">週 K 線</button>
                        </div>
                        <button class="btn btn-outline-primary btn-sm fw-bold shadow-sm" @click="toggleYearChart(yearData.year)">
                            {{ activeChartYear === yearData.year ? '收合圖表 🔼' : '📊 展開本年度 K 線圖 🔽' }}
                        </button>
                    </div>
                </div>

                <div v-show="activeChartYear === yearData.year" class="card shadow-sm border-primary mb-4 overflow-hidden">
                    <div class="card-header bg-primary text-white py-2 fw-bold text-center d-flex justify-content-between">
                        <span>{{ yearData.year }} 年台股走勢圖</span>
                        <span class="badge bg-white text-primary">{{ chartPeriodType === 'daily' ? '日線模式' : '週線模式' }}</span>
                    </div>
                    <div class="card-body bg-white p-2">
                        <div :id="'chart-year-' + yearData.year" style="width: 100%; height: 500px;"></div>
                    </div>
                </div>

                <div class="table-responsive bg-white rounded shadow-sm border">
                    <table class="table table-hover table-striped mb-0 text-center align-middle">
                        <thead class="table-light">
                            <tr>
                                <th>交叉日期</th>
                                <th>轉折類型</th>
                                <th>當時指數</th>
                                <th>前波段交易天數</th>
                                <th>前波段空間結算</th>
                                <th>較年代極值 (均標)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(cross, idx) in yearData.crosses" :key="idx">
                                <td class="text-muted">{{ cross.date }}</td>
                                <td>
                                    <span v-if="cross.type === 'golden'" class="badge bg-danger rounded-pill px-3 py-2">🔥 黃金交叉 (起漲)</span>
                                    <span v-else class="badge bg-success rounded-pill px-3 py-2">❄️ 死亡交叉 (起跌)</span>
                                </td>
                                <td class="fw-bold">{{ cross.price.toFixed(0) }}</td>
                                <td>
                                    <span class="fw-bold text-dark">{{ cross.tradingDays > 0 ? cross.tradingDays + ' 天' : '--' }}</span>
                                </td>
                                <td>
                                    <span v-if="cross.change > 0" class="fw-bold text-danger">📈 上漲 {{ cross.change.toFixed(0) }} 點</span>
                                    <span v-else-if="cross.change < 0" class="fw-bold text-success">📉 下跌 {{ Math.abs(cross.change).toFixed(0) }} 點</span>
                                    <span v-else class="text-muted">--</span>
                                </td>
                                <td>
                                    <div v-if="cross.change > 0 && activeAvgUp > 0">
                                        <span :class="cross.change > activeAvgUp ? 'text-danger fw-bold' : 'text-secondary'">
                                            {{ cross.change >= activeAvgUp ? '+' : '' }}{{ (cross.change - activeAvgUp).toFixed(0) }} 點
                                        </span>
                                        <div class="text-muted mt-1" style="font-size: 0.75rem;">(達均標 {{ ((cross.change / activeAvgUp) * 100).toFixed(1) }}%)</div>
                                    </div>
                                    <div v-else-if="cross.change < 0 && activeAvgDown > 0">
                                        <span :class="Math.abs(cross.change) > activeAvgDown ? 'text-success fw-bold' : 'text-secondary'">
                                            {{ Math.abs(cross.change) >= activeAvgDown ? '+' : '' }}{{ (Math.abs(cross.change) - activeAvgDown).toFixed(0) }} 點
                                        </span>
                                        <div class="text-muted mt-1" style="font-size: 0.75rem;">(達均標 {{ ((Math.abs(cross.change) / activeAvgDown) * 100).toFixed(1) }}%)</div>
                                    </div>
                                    <span v-else class="text-muted">--</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

            </div>
          </div>
        </div>
      </div>
      
    </div>
    
    <div v-if="!isLoading && !groupedData[activeDecade]" class="text-center my-5 text-muted fw-bold">
        該年代無 API 歷史數據 (或尚未載入)。
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'

const isLoading = ref(true);
const errorMsg = ref('');
const rawCrosses = ref([]);

const fullWeeklyData = ref([]); 
const fullDailyData = ref([]);

const activeDecade = ref('2020');
const activeChartYear = ref(null);
const chartPeriodType = ref('weekly'); 
let chartInstanceMap = {};

const availableDecades = [
    { id: '1980', label: '1980 - 1989' },
    { id: '1990', label: '1990 - 1999' },
    { id: '2000', label: '2000 - 2009' },
    { id: '2010', label: '2010 - 2019' },
    { id: '2020', label: '2020 - 2026' }
];

const sanitize = (q) => {
    if (!q || !Array.isArray(q)) return [];
    return q.filter(x => x.open != null && x.close != null && !isNaN(x.close));
};

const calcKD = (q) => {
    let k=50, d=50;
    return q.map((x, i, a) => {
        if(i<8) return {...x, k:50, d:50};
        const r = a.slice(i-8, i+1);
        const h = Math.max(...r.map(v=>v.high));
        const l = Math.min(...r.map(v=>v.low));
        let rsv = h === l ? 50 : ((x.close-l)/(h-l))*100;
        k = (rsv + k*2)/3; 
        d = (k + d*2)/3;
        return {...x, k, d};
    });
};

const calcMA = (n, q) => q.map((_, i, a) => i < n-1 ? null : a.slice(i-n+1, i+1).reduce((s, x)=>s+x.close,0)/n);

onMounted(async () => {
    try {
        const res = await $fetch('/api/macrowave/taiex');
        if (!res || !res.success) throw new Error(res?.message || '資料獲取失敗');
        
        const safeWeekly = sanitize(res.data.weekly);
        const safeDaily = sanitize(res.data.daily);

        if (safeWeekly.length === 0 || safeDaily.length === 0) throw new Error('API 傳回的數據為空');

        const weeklyKD = calcKD(safeWeekly);
        const dailyKD = calcKD(safeDaily);
        fullWeeklyData.value = weeklyKD;
        fullDailyData.value = dailyKD;

        const dailyDateArray = safeDaily.map(d => d.date);

        const crosses = [];
        let lastCrossPrice = null;
        let lastCrossType = null;
        let lastCrossDate = null;

        for (let i = 1; i < weeklyKD.length; i++) {
            const p = weeklyKD[i-1], c = weeklyKD[i];
            if (p.k == null || p.d == null || c.k == null || c.d == null) continue;

            let crossType = null;
            if (p.k <= p.d && c.k > c.d) crossType = 'golden';
            if (p.k >= p.d && c.k < c.d) crossType = 'death';

            if (crossType && crossType !== lastCrossType) {
                const year = new Date(c.date).getFullYear();
                let pointChange = 0;
                let tradingDays = 0;
                
                if (lastCrossPrice !== null && lastCrossDate !== null) {
                    pointChange = c.close - lastCrossPrice;
                    tradingDays = dailyDateArray.filter(d => d > lastCrossDate && d <= c.date).length;
                }

                crosses.push({
                    date: c.date,
                    year: year,
                    type: crossType,
                    price: c.close,
                    change: pointChange,
                    tradingDays: tradingDays
                });

                lastCrossPrice = c.close;
                lastCrossType = crossType;
                lastCrossDate = c.date;
            }
        }
        
        rawCrosses.value = crosses.reverse();

        if (rawCrosses.value.length > 0) {
            const latestYear = rawCrosses.value[0].year;
            const decadeFloor = Math.floor(latestYear / 10) * 10;
            activeDecade.value = decadeFloor.toString();
        }

    } catch (err) {
        errorMsg.value = err.message || '回測運算發生錯誤';
    } finally {
        isLoading.value = false;
    }
});

// 資料分組邏輯
const groupedData = computed(() => {
    const groups = { '1980': [], '1990': [], '2000': [], '2010': [], '2020': [] };
    
    Object.keys(groups).forEach(dec => {
        const start = parseInt(dec);
        for(let y = start + 9; y >= start; y--) {
            if(y > 2026) continue;
            groups[dec].push({ year: y, crosses: [] });
        }
    });

    rawCrosses.value.forEach(cross => {
        const decadeKey = (Math.floor(cross.year / 10) * 10).toString();
        if (groups[decadeKey]) {
            const yearGroup = groups[decadeKey].find(g => g.year === cross.year);
            if (yearGroup) yearGroup.crosses.push(cross);
        }
    });

    Object.keys(groups).forEach(dec => {
        groups[dec] = groups[dec].filter(g => g.crosses.length > 0);
        if (groups[dec].length === 0) delete groups[dec];
    });

    return groups;
});

// 🔥 新增：精算本年代平均多頭(漲點)與平均空頭(跌點)
const activeAvgUp = computed(() => {
    const data = groupedData.value[activeDecade.value];
    if (!data) return 0;
    let sum = 0, count = 0;
    data.forEach(y => y.crosses.forEach(c => {
        if (c.change > 0) { sum += c.change; count++; }
    }));
    return count ? sum / count : 0;
});

const activeAvgDown = computed(() => {
    const data = groupedData.value[activeDecade.value];
    if (!data) return 0;
    let sum = 0, count = 0;
    data.forEach(y => y.crosses.forEach(c => {
        if (c.change < 0) { sum += Math.abs(c.change); count++; }
    }));
    return count ? sum / count : 0;
});

const getDecadeAvgCrosses = (decade) => {
    const data = groupedData.value[decade];
    if (!data || data.length === 0) return 0;
    const totalCrosses = data.reduce((sum, yData) => sum + yData.crosses.length, 0);
    return (totalCrosses / data.length).toFixed(1);
};
const getDecadeBestWave = (decade) => {
    const data = groupedData.value[decade];
    if (!data) return 0;
    let max = 0;
    data.forEach(y => y.crosses.forEach(c => { if (c.change > max) max = c.change; }));
    return max.toFixed(0);
};
const getDecadeWorstWave = (decade) => {
    const data = groupedData.value[decade];
    if (!data) return 0;
    let min = 0;
    data.forEach(y => y.crosses.forEach(c => { if (c.change < min) min = c.change; }));
    return min.toFixed(0);
};

// ==========================================
// 圖表繪製與切換邏輯
// ==========================================

const changeChartPeriod = async (type, year) => {
    chartPeriodType.value = type;
    await nextTick();
    renderYearChart(year);
};

const toggleYearChart = async (year) => {
    if (activeChartYear.value === year) {
        activeChartYear.value = null; 
        return;
    }
    
    activeChartYear.value = year;
    chartPeriodType.value = 'weekly';
    await nextTick();
    renderYearChart(year);
};

const renderYearChart = (year) => {
    const domId = 'chart-year-' + year;
    const dom = document.getElementById(domId);
    
    if (!dom || !echarts) {
        alert('圖表庫尚未準備好，請稍後再試');
        return;
    }

    const isDaily = chartPeriodType.value === 'daily';
    const sourceData = isDaily ? fullDailyData.value : fullWeeklyData.value;
    
    const yearData = sourceData.filter(d => d.date.startsWith(year.toString()));
    if (yearData.length === 0) return;

    const categoryData = yearData.map(item => item.date);
    const candleValues = yearData.map(item => [item.open, item.close, item.low, item.high]);
    const volumeData = yearData.map(item => ({
        value: item.volume || 0,
        itemStyle: { color: item.close >= item.open ? '#dc3545' : '#198754' }
    }));
    const kData = yearData.map(item => item.k);
    const dData = yearData.map(item => item.d);

    const ma20 = isDaily ? calcMA(20, yearData) : [];
    const ma60 = isDaily ? calcMA(60, yearData) : [];

    const kdMarks = [];
    for (let i = 1; i < yearData.length; i++) {
        const p = yearData[i - 1], c = yearData[i];
        if (p.k <= p.d && c.k > c.d) {
            kdMarks.push({ coord: [i, c.k], symbol: 'arrow', symbolSize: 12, itemStyle: { color: '#dc3545' }, value: '金叉' });
        }
        if (p.k >= p.d && c.k < c.d) {
            kdMarks.push({ coord: [i, c.k], symbol: 'arrow', symbolRotate: 180, symbolSize: 12, itemStyle: { color: '#198754' }, value: '死叉' });
        }
    }

    if (chartInstanceMap[domId]) chartInstanceMap[domId].dispose();
    const inst = echarts.init(dom);
    chartInstanceMap[domId] = inst;

    inst.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        axisPointer: { link: [{ xAxisIndex: 'all' }] },
        legend: { 
            data: isDaily ? ['日 K線', '20MA', '60MA', '成交量', 'K值', 'D值'] : ['週 K線', '成交量', 'K值', 'D值'], 
            top: 5 
        },
        grid: [
            { left: '6%', right: '5%', top: '10%', height: '45%' },
            { left: '6%', right: '5%', top: '60%', height: '15%' },
            { left: '6%', right: '5%', top: '80%', height: '15%' }
        ],
        xAxis: [
            { type: 'category', data: categoryData, gridIndex: 0, axisLabel: { show: false } },
            { type: 'category', data: categoryData, gridIndex: 1, axisLabel: { show: false } },
            { type: 'category', data: categoryData, gridIndex: 2 }
        ],
        yAxis: [
            { scale: true, gridIndex: 0 },
            { scale: true, gridIndex: 1, axisLabel: { show: false } },
            { min: 0, max: 100, gridIndex: 2, splitLine: { show: true, lineStyle: { type: 'dashed' } } }
        ],
        dataZoom: [{ type: 'inside', xAxisIndex: [0, 1, 2] }, { show: true, xAxisIndex: [0, 1, 2], top: '96%', height: 15 }], 
        series: [
            { 
                name: isDaily ? '日 K線' : '週 K線', 
                type: 'candlestick', 
                data: candleValues, 
                itemStyle: { color: '#dc3545', color0: '#198754', borderColor: '#dc3545', borderColor0: '#198754' } 
            },
            ...(isDaily ? [
                { name: '20MA', type: 'line', data: ma20, smooth: true, symbol: 'none', lineStyle: { color: '#0dcaf0' } },
                { name: '60MA', type: 'line', data: ma60, smooth: true, symbol: 'none', lineStyle: { color: '#ffc107' } }
            ] : []),
            { name: '成交量', type: 'bar', data: volumeData, xAxisIndex: 1, yAxisIndex: 1 },
            { name: 'K值', type: 'line', data: kData, xAxisIndex: 2, yAxisIndex: 2, lineStyle: { color: '#dc3545' }, markPoint: { data: kdMarks, label: {show:false} } },
            { name: 'D值', type: 'line', data: dData, xAxisIndex: 2, yAxisIndex: 2, lineStyle: { color: '#0d6efd' } }
        ]
    });
};
</script>

<style scoped>
.accordion-button:not(.collapsed) {
    background-color: #d1e7dd;
    color: #0f5132;
    box-shadow: none;
}
.accordion-button:focus {
    border-color: #198754;
    box-shadow: 0 0 0 0.25rem rgba(25, 135, 84, 0.25);
}
</style>
