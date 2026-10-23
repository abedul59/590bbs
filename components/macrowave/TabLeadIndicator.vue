<template>
  <div class="container-fluid pb-5 mt-4">
    <div class="row mb-4">
      <div class="col-12">
        <div class="card shadow-sm border-0 bg-dark text-white">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <h4 class="fw-bold mb-1">📊 台灣領先指標 ╳ 0050 總經戰情室</h4>
              <p class="text-secondary mb-0 small">
                自動化量化策略：景氣分數 ≤ 22 且回升 (或指標 > 100) 買進；指標 < 100 且下滑賣出。
              </p>
            </div>
            <div class="text-end" v-if="!isLoading && chartDataList.length > 0">
              <span class="badge bg-secondary fs-6 me-2">回測筆數：{{ chartDataList.length }} 個月</span>
              <span class="badge bg-primary fs-6">觸發交易：{{ trades.length }} 次</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="text-center my-5 py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status"></div>
      <h5 class="mt-4 fw-bold text-primary">系統正在載入並清洗回測數據...</h5>
    </div>

    <div v-if="errorMsg" class="alert alert-danger shadow-sm fw-bold text-center fs-5">
      ❌ 讀取失敗：{{ errorMsg }}
    </div>

    <div v-show="!isLoading && chartDataList.length > 0" class="row">
      <div class="col-lg-12 mb-4">
        <div class="card shadow-sm border-0 h-100">
          <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between">
            <span class="text-dark">📈 策略回測圖表 (支援滾輪縮放)</span>
            <span class="badge bg-success">🟢 買進標記</span>
            <span class="badge bg-danger">🔴 賣出標記</span>
          </div>
          <div class="card-body p-2">
            <div id="chart-lead-0050" style="width: 100%; height: 800px;"></div>
          </div>
        </div>
      </div>

      <div class="col-lg-12">
        <div class="card shadow-sm border-0">
          <div class="card-header bg-white fw-bold py-3 d-flex justify-content-between align-items-center">
            <span class="text-dark">📜 歷史所有數據明細 (由新到舊)</span>
            <span class="badge bg-light text-dark border">展開所有月份數據</span>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
              <table class="table table-hover table-striped mb-0 text-center align-middle">
                <thead class="table-dark sticky-top">
                  <tr>
                    <th>交易年月</th>
                    <th>信號動作</th>
                    <th>收盤價 (0050)</th>
                    <th>領先指標</th>
                    <th>景氣分數</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in chartDataList.slice().reverse()" :key="index">
                    <td class="fw-bold">{{ item.date }}</td>
                    
                    <td>
                      <span v-if="item.action === 'BUY'" class="badge bg-success fs-6">買進 (BUY)</span>
                      <span v-else-if="item.action === 'SELL'" class="badge bg-danger fs-6">賣出 (SELL)</span>
                      <span v-else class="text-muted">-</span>
                    </td>
                    
                    <td :class="{'fw-bold text-primary': item.action, 'text-dark': !item.action}">
                      {{ item.close.toFixed(2) }}
                    </td>
                    <td :class="{'fw-bold': item.action}">{{ item.lead.toFixed(2) }}</td>
                    <td>
                      <span :class="item.score <= 22 ? 'text-primary fw-bold' : 'text-dark'">
                        {{ item.score }}
                      </span>
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
</template>

<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue';
import * as echarts from 'echarts';

const isLoading = ref(true);
const errorMsg = ref('');
const chartDataList = ref([]); 
const trades = ref([]); 
let chartInstance = null;
let resizeObserver = null; // 🔥 新增：元素尺寸監聽器

const supabase = useSupabaseClient();

const loadBundledFallbackData = async () => {
  const staticData = await $fetch('/macrowave-lead-data.json').catch(() => null);
  if (staticData?.length) return staticData;

  const [indicators, priceResponse] = await Promise.all([
    $fetch('/macrowave-leading-indicators.json'),
    $fetch('/api/macrowave/lead')
  ]);

  const pricesByPeriod = new Map(
    (priceResponse?.data || []).map(item => [item.period, Number(item.close)])
  );

  const combined = (indicators || [])
    .map(item => ({
      date: `${item.period}-01`,
      close: pricesByPeriod.get(item.period),
      lead: Number(item.lead),
      score: Number(item.score)
    }))
    .filter(item => Number.isFinite(item.close));

  if (!combined.length) {
    throw new Error('0050 與台灣領先指標的月資料無法對齊。');
  }
  return combined;
};

const loadLeadIndicatorData = async () => {
  // 原 MacroWave 網站的歷史資料存在 macro_lead_0050。
  // 保留新表名做為備援，避免未來搬遷後再次斷資料。
  const tableNames = ['macro_lead_0050', 'macrowave_lead_0050'];
  const failures = [];

  for (const tableName of tableNames) {
    const { data, error } = await supabase
      .from(tableName)
      .select('*')
      .order('date', { ascending: true });

    if (error) {
      failures.push(`${tableName}: ${error.message}`);
      continue;
    }
    if (data?.length) return data;
  }

  try {
    return await loadBundledFallbackData();
  } catch (fallbackError) {
    const databaseDetail = failures.length ? `資料庫：${failures.join(' / ')}；` : '';
    throw new Error(`${databaseDetail}備援資料：${fallbackError.message}`);
  }
};

onMounted(async () => {
  try {
    isLoading.value = true;
    const data = await loadLeadIndicatorData();

    const cleanData = [];
    data.forEach(item => {
      const d = item.date ? String(item.date).split('T')[0] : '';
      if (!d) return;

      const c = Number(item.close);
      if (isNaN(c)) return; 

      let lead = Number(item.lead); if (isNaN(lead)) lead = 0;
      let score = Number(item.score); if (isNaN(score)) score = 0;

      cleanData.push({
        date: d,
        close: c,
        lead: lead,
        score: score
      });
    });

    let currentPosition = 1; 
    const processedData = [];
    const tradeRecords = [];

    for (let i = 0; i < cleanData.length; i++) {
      const row = cleanData[i];
      const prevRow = i > 0 ? cleanData[i - 1] : row;
      const leadDiff = row.lead - prevRow.lead;
      
      let signal = null;
      if ((row.score <= 22 && leadDiff > 0) || row.lead > 100) {
        signal = 1;
      } else if (row.lead < 100 && leadDiff < 0) {
        signal = 0;
      }

      if (signal !== null) {
        currentPosition = signal;
      }

      let currentAction = null;

      if (i > 0) {
        const prevPosition = processedData[i - 1].position;
        if (currentPosition === 1 && prevPosition === 0) {
          currentAction = 'BUY';
          tradeRecords.push({ date: row.date, type: 'BUY', price: row.close, lead: row.lead, score: row.score });
        } else if (currentPosition === 0 && prevPosition === 1) {
          currentAction = 'SELL';
          tradeRecords.push({ date: row.date, type: 'SELL', price: row.close, lead: row.lead, score: row.score });
        }
      }

      processedData.push({ ...row, position: currentPosition, action: currentAction });
    }

    chartDataList.value = processedData;
    trades.value = tradeRecords;

    // 等待 Vue 將 DOM 完全渲染到畫面上
    await nextTick();
    
    // 🔥 加上微小的延遲，確保 CSS Flex/Grid 已經把容器寬度撐開
    setTimeout(() => {
      renderChart(processedData, tradeRecords);
    }, 100);

    window.addEventListener('resize', handleResize);

  } catch (err) {
    console.error('資料讀取錯誤:', err);
    errorMsg.value = err.message;
  } finally {
    isLoading.value = false;
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  // 🔥 關閉時記得解除監聽，避免記憶體洩漏
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
  if (chartInstance) chartInstance.dispose();
});

const handleResize = () => {
  if (chartInstance) chartInstance.resize();
};

const renderChart = (data, tradeRecords) => {
  const dom = document.getElementById('chart-lead-0050');
  if (!dom) return;

  if (chartInstance) chartInstance.dispose();
  chartInstance = echarts.init(dom);

  // 🔥 終極保險：使用 ResizeObserver 緊迫盯人
  // 只要那個 div 元素的寬度或高度一發生變化，立刻叫 ECharts 重繪
  if (!resizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      if (chartInstance) chartInstance.resize();
    });
    resizeObserver.observe(dom);
  }

  const dates = [];
  const priceData = []; 
  const leadData = [];

  data.forEach(item => {
    dates.push(item.date);
    priceData.push(item.close); 
    leadData.push(item.lead);
  });

  const priceMarks = tradeRecords.map(t => ({
    xAxis: t.date,
    yAxis: t.price,
    value: t.type,
    symbol: t.type === 'BUY' ? 'arrow' : 'pin',
    symbolSize: 16,
    symbolRotate: t.type === 'BUY' ? 0 : 180,
    symbolOffset: [0, t.type === 'BUY' ? 15 : -15],
    itemStyle: { color: t.type === 'BUY' ? '#198754' : '#dc3545' },
    label: { show: false }
  }));

  const leadMarks = tradeRecords.map(t => ({
    xAxis: t.date,
    yAxis: t.lead,
    value: t.type,
    symbol: t.type === 'BUY' ? 'arrow' : 'pin',
    symbolSize: 16,
    symbolRotate: t.type === 'BUY' ? 0 : 180,
    symbolOffset: [0, t.type === 'BUY' ? 15 : -15],
    itemStyle: { color: t.type === 'BUY' ? '#198754' : '#dc3545' },
    label: { show: false }
  }));

  const holdingAreas = [];
  let startHoldDate = null;
  for (let i = 0; i < data.length; i++) {
    if (data[i].position === 1 && startHoldDate === null) {
      startHoldDate = data[i].date;
    } else if (data[i].position === 0 && startHoldDate !== null) {
      holdingAreas.push([{ xAxis: startHoldDate }, { xAxis: data[i - 1].date }]);
      startHoldDate = null;
    }
  }
  if (startHoldDate !== null) {
    holdingAreas.push([{ xAxis: startHoldDate }, { xAxis: data[data.length - 1].date }]);
  }

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    axisPointer: { link: [{ xAxisIndex: 'all' }] },
    legend: { data: ['0050 月收盤走勢', '領先指標'], top: 10 },
    grid: [
      { left: '8%', right: '5%', top: '10%', height: '50%' }, 
      { left: '8%', right: '5%', top: '68%', height: '25%' }  
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
      { type: 'category', data: dates, gridIndex: 1 }
    ],
    yAxis: [
      { type: 'value', scale: true, gridIndex: 0, name: '股價 (元)' },
      { type: 'value', scale: true, gridIndex: 1, name: '指標分數' }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
      { show: true, xAxisIndex: [0, 1], top: '95%', height: 15 }
    ],
    series: [
      {
        name: '0050 月收盤走勢',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: priceData,
        lineStyle: { color: '#212529', width: 2 }, 
        showSymbol: false, 
        itemStyle: { color: '#212529' },
        markPoint: {
          data: priceMarks
        }
      },
      {
        name: '領先指標',
        type: 'line',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: leadData,
        lineStyle: { color: '#0d6efd', width: 2 },
        showSymbol: true,
        symbol: 'circle',
        symbolSize: 5,
        itemStyle: { color: '#0d6efd' },
        markPoint: {
          data: leadMarks 
        },
        markLine: {
          symbol: 'none',
          data: [{ yAxis: 100, name: '100 基準線', lineStyle: { color: '#dc3545', type: 'dashed' } }]
        },
        markArea: {
          itemStyle: { color: 'rgba(253, 126, 20, 0.2)' },
          data: holdingAreas
        }
      }
    ]
  };

  chartInstance.setOption(option, true);
  
  // 🔥 強制再次校準：確保第一次畫上去後，馬上依照最終寬度重繪
  chartInstance.resize();
};
</script>
