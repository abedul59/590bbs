<template>
  <div class="container pb-5 mt-4">
    
    <div class="card shadow-sm border-0 mb-4 bg-light">
      <div class="card-body">
        <h5 class="fw-bold text-primary mb-2">🔥 微台指散戶多空比 ╳ 價格 戰情室</h5>
        <p class="text-muted small mb-0">
          資料來源：Supabase 雲端關聯式資料庫。支援極速渲染與安全連線。
        </p>
      </div>
    </div>

    <div v-if="isLoading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-3 fw-bold text-primary">連線至 Supabase 資料庫，讀取籌碼中...</p>
    </div>

    <div v-if="errorMsg" class="alert alert-danger fw-bold text-center">
      ❌ 讀取失敗：{{ errorMsg }}
    </div>

    <div v-if="!isLoading && historyList.length > 0">
        
        <div class="card shadow-sm border-0 mb-4">
            <div class="card-header bg-white p-3">
                <div class="row align-items-center">
                    <div class="col-md-4 mb-2 mb-md-0">
                        <span class="fw-bold">📈 價格走勢與散戶籌碼對照圖</span>
                        <span class="badge bg-primary ms-2">滾輪縮放</span>
                    </div>
                    <div class="col-md-8 d-flex justify-content-md-end align-items-center gap-3 flex-wrap">
                        <div class="input-group input-group-sm" style="max-width: 180px;">
                            <span class="input-group-text bg-danger text-white fw-bold">買進界線</span>
                            <input type="number" class="form-control text-center" v-model.number="buyThreshold" @change="updateThresholds">
                            <span class="input-group-text">%</span>
                        </div>
                        <div class="input-group input-group-sm" style="max-width: 180px;">
                            <span class="input-group-text bg-success text-white fw-bold">賣出界線</span>
                            <input type="number" class="form-control text-center" v-model.number="sellThreshold" @change="updateThresholds">
                            <span class="input-group-text">%</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-body p-2">
                <div id="chart-tmf" style="width: 100%; height: 600px;"></div>
            </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
            <div class="card-header bg-secondary text-white fw-bold d-flex justify-content-between">
                <span>📜 雲端資料庫明細</span>
                <span class="badge bg-light text-dark">共 {{ historyList.length }} 筆資料</span>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
                    <table class="table table-hover table-striped mb-0 text-center align-middle" style="font-size: 0.9rem;">
                        <thead class="table-light sticky-top">
                            <tr>
                                <th>交易日期</th>
                                <th>收盤價</th>
                                <th>散戶多空比</th>
                                <th>散戶淨未平倉 (OI)</th>
                                <th>全市場總 OI</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in historyList" :key="item.date">
                                <td class="text-muted fw-bold">{{ item.date }}</td>
                                <td class="text-dark fw-bold">{{ item.close.toLocaleString() }}</td>
                                <td :class="['fw-bold', item.retailRatio < 0 ? 'text-success' : 'text-danger']">
                                    {{ (item.retailRatio * 100).toFixed(2) }}%
                                </td>
                                <td :class="item.retailNetOI > 0 ? 'text-danger' : 'text-success'">
                                    {{ item.retailNetOI.toLocaleString() }} 口
                                </td>
                                <td class="text-muted font-monospace">{{ item.totalOI.toLocaleString() }} 口</td>
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
import { ref, onMounted, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const isLoading = ref(true);
const errorMsg = ref('');
const historyList = ref([]);
let chartInstance = null;

// 🔥 新增：綁定買賣界線的預設值 (可動態修改)
const buyThreshold = ref(-10);
const sellThreshold = ref(15);

const supabase = useSupabaseClient();

onMounted(async () => {
    try {
        isLoading.value = true;
        
        const { data, error } = await supabase
            .from('macrowave_tmf_data')
            .select('*')
            .order('date', { ascending: false });

        if (error) {
            throw new Error(error.message);
        }

        if (!data || data.length === 0) {
            throw new Error('Supabase 資料庫中目前無數據。');
        }

        historyList.value = data.map(row => ({
            date: row.date,
            totalOI: row.total_oi,
            instNetOI: row.inst_net_oi,
            retailNetOI: row.retail_net_oi,
            retailRatio: row.retail_ratio,
            open: row.open,
            high: row.high,
            low: row.low,
            close: row.close
        }));
        
    } catch (err) {
        console.error('Supabase 讀取錯誤:', err);
        errorMsg.value = err.message || '無法連線至 Supabase 資料庫';
    } finally {
        isLoading.value = false;
        
        if (historyList.value.length > 0) {
            await nextTick();
            const chartData = [...historyList.value].reverse();
            renderChart(chartData);
        }
    }
    
    window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize);
    if (chartInstance) {
        chartInstance.dispose();
    }
});

const handleResize = () => {
    if (chartInstance) {
        chartInstance.resize();
    }
};

// 🔥 新增：當使用者修改界線值後，重新觸發繪圖函數更新畫面
const updateThresholds = () => {
    if (historyList.value.length > 0) {
        const chartData = [...historyList.value].reverse();
        renderChart(chartData);
    }
};

const renderChart = (data) => {
    const dom = document.getElementById('chart-tmf');
    if (!dom) return;

    if (chartInstance) {
        chartInstance.dispose();
    }
    
    chartInstance = echarts.init(dom);

    const categoryData = data.map(item => item.date);
    const candleValues = data.map(item => [item.open, item.close, item.low, item.high]);
    
    const ratioData = data.map(item => {
        const val = item.retailRatio * 100;
        return {
            value: val.toFixed(2),
            itemStyle: { color: val < 0 ? '#198754' : '#dc3545' } 
        };
    });

    chartInstance.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        axisPointer: { link: [{ xAxisIndex: 'all' }] },
        legend: { data: ['價格 K 線', '散戶多空比'], top: 5 },
        grid: [
            { left: '8%', right: '5%', top: '8%', height: '50%' },
            { left: '8%', right: '5%', top: '65%', height: '25%' }
        ],
        xAxis: [
            { type: 'category', data: categoryData, gridIndex: 0, axisLabel: { show: false } },
            { type: 'category', data: categoryData, gridIndex: 1 }
        ],
        yAxis: [
            { scale: true, gridIndex: 0 },
            { type: 'value', gridIndex: 1, name: '多空比(%)', splitLine: { show: true, lineStyle: { type: 'dashed' } } }
        ],
        dataZoom: [
            { type: 'inside', xAxisIndex: [0, 1], start: 70, end: 100 }, 
            { show: true, xAxisIndex: [0, 1], top: '92%', height: 15 }
        ], 
        series: [
            { 
                name: '價格 K 線', type: 'candlestick', xAxisIndex: 0, yAxisIndex: 0, data: candleValues, 
                itemStyle: { color: '#dc3545', color0: '#198754', borderColor: '#dc3545', borderColor0: '#198754' } 
            },
            {
                name: '散戶多空比', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: ratioData,
                markLine: {
                    symbol: 'none',
                    label: { position: 'insideEndTop', formatter: '{b}' },
                    data: [
                        // 🔥 關鍵連動：使用 v-model 綁定的動態變數繪製標記線
                        { yAxis: buyThreshold.value, name: '買進', lineStyle: { color: '#dc3545', type: 'solid', width: 2 } },
                        { yAxis: sellThreshold.value, name: '賣出', lineStyle: { color: '#198754', type: 'solid', width: 2 } }
                    ]
                }
            }
        ]
    });
};
</script>
