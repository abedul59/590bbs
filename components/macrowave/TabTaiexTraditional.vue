<template>
  <div class="container pb-5 mt-4">
    
    <div v-if="errorMsg" class="alert alert-danger text-center shadow-sm fw-bold my-4">
        ❌ 系統錯誤：{{ errorMsg }}
    </div>

    <div class="row mb-4" v-if="analysis">
      <div class="col-12 mb-3">
          <div class="alert alert-secondary border-secondary shadow-sm">
              ℹ️ <strong>傳統極值標準 (適用於大盤萬點以下)：</strong> 月線極值看 2,000 點；週線極值看 600~800 點。
          </div>
      </div>
      
      <div class="col-md-6 mb-3">
        <div class="card h-100 border-primary shadow-sm">
          <div class="card-header bg-primary text-white fw-bold d-flex justify-content-between">
              <span>長線循環：月KD ╳ 季線</span><span>最新: {{ analysis.daily.current.toFixed(0) }}</span>
          </div>
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">最新月 KD</span><span class="fw-bold fs-5">K: <span :class="analysis.monthly.k > 80 ? 'text-danger' : ''">{{ analysis.monthly.k.toFixed(2) }}</span> / D: {{ analysis.monthly.d.toFixed(2) }}</span>
            </div>
            <div class="d-flex justify-content-between mb-3">
              <span class="text-muted">季線 (60MA) 現況</span><span class="fw-bold fs-5">{{ analysis.daily.ma60.toFixed(2) }} <span v-html="analysis.daily.ma60_trend"></span></span>
            </div>
            <div class="bg-light p-3 rounded border border-warning mb-3">
              <div class="fw-bold text-dark mb-1">🎯 季線 (60MA) 扣抵預測</div>
              <div class="d-flex justify-content-between small"><span>明日均線防守價</span><span class="fw-bold">{{ analysis.daily.deduction60.price.toFixed(2) }}</span></div>
              <div class="d-flex justify-content-between align-items-center mt-2">
                <span class="small">多空判定：</span>
                <span v-if="analysis.daily.deduction60.isSafe" class="badge bg-success">安全 (+{{ analysis.daily.deduction60.diff.toFixed(0) }})</span>
                <span v-else class="badge bg-danger">警戒 ({{ analysis.daily.deduction60.diff.toFixed(0) }})</span>
              </div>
            </div>
            <hr class="mt-auto">
            <p class="text-muted small mb-0">{{ analysis.monthly.analysisTxt }}</p>
            <div class="alert mt-2 mb-0 py-2 fw-bold text-center" :class="analysis.monthly.alertClass">{{ analysis.monthly.alertText }}</div>
          </div>
        </div>
      </div>

      <div class="col-md-6 mb-3">
        <div class="card h-100 border-info shadow-sm">
          <div class="card-header bg-info text-dark fw-bold d-flex justify-content-between">
              <span>中線行情：週KD ╳ 月線</span><span>最新: {{ analysis.daily.current.toFixed(0) }}</span>
          </div>
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">最新週 KD</span><span class="fw-bold fs-5">K: <span :class="analysis.weekly.k > 80 ? 'text-danger' : ''">{{ analysis.weekly.k.toFixed(2) }}</span> / D: {{ analysis.weekly.d.toFixed(2) }}</span>
            </div>
            <div class="d-flex justify-content-between mb-3">
              <span class="text-muted">月線 (20MA) 現況</span><span class="fw-bold fs-5">{{ analysis.daily.ma20.toFixed(2) }} <span v-html="analysis.daily.ma20_trend"></span></span>
            </div>
            <div class="bg-light p-3 rounded border border-primary mb-3">
              <div class="fw-bold text-dark mb-1">🎯 月線 (20MA) 扣抵預測</div>
              <div class="d-flex justify-content-between small"><span>明日均線防守價</span><span class="fw-bold">{{ analysis.daily.deduction20.price.toFixed(2) }}</span></div>
              <div class="d-flex justify-content-between align-items-center mt-2">
                <span class="small">多空判定：</span>
                <span v-if="analysis.daily.deduction20.isSafe" class="badge bg-success">安全 (+{{ analysis.daily.deduction20.diff.toFixed(0) }})</span>
                <span v-else class="badge bg-danger">警戒 ({{ analysis.daily.deduction20.diff.toFixed(0) }})</span>
              </div>
            </div>
            <hr class="mt-auto">
            <p class="text-muted small mb-0">{{ analysis.weekly.analysisTxt }}</p>
            <div class="alert mt-2 mb-0 py-2 fw-bold text-center" :class="analysis.weekly.alertClass">{{ analysis.weekly.alertText }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="isLoading && !errorMsg" class="text-center my-5"><div class="spinner-border text-primary"></div><p class="mt-2 fw-bold">傳統極值運算中...</p></div>

    <div class="card shadow-sm mb-4" v-show="!isLoading && taiexData && !errorMsg">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
          <h5 class="fw-bold text-secondary mb-0">台股加權指數 (^TWII)</h5>
          <div class="btn-group mt-2 mt-md-0">
            <button v-for="p in ['daily', 'weekly', 'monthly']" :key="p" @click="currentPeriod = p; renderChart()" :class="['btn fw-bold', currentPeriod === p ? 'btn-primary' : 'btn-outline-primary']">{{ p === 'daily' ? '日 K' : p === 'weekly' ? '週 K' : '月 K' }}</button>
          </div>
        </div>
        <div id="taiexChartTrad" style="width: 100%; height: 75vh; min-height: 550px;"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const isLoading = ref(true);
const errorMsg = ref('');
const taiexData = ref(null);
const analysis = ref(null);
const currentPeriod = ref('daily');
let chartInstance = null;

const sanitize = (q) => {
    if (!q || !Array.isArray(q)) return [];
    return q.filter(x => x.open != null && x.close != null && !isNaN(x.close));
};

const calcKD = (q) => {
    let k=50, d=50;
    return q.map((x, i, a) => {
        if(i<8) return {...x, k:50, d:50};
        const r = a.slice(i-8, i+1), h = Math.max(...r.map(v=>v.high)), l = Math.min(...r.map(v=>v.low));
        let rsv = h===l ? 0 : ((x.close-l)/(h-l))*100;
        k = (rsv+k*2)/3; d = (k+d*2)/3;
        return {...x, k, d};
    });
};

const calcMA = (n, q) => q.map((_, i, a) => i < n-1 ? null : a.slice(i-n+1, i+1).reduce((s, x)=>s+x.close,0)/n);

const findCross = (kd) => {
    if (!kd || kd.length < 2) return null;
    for(let i = kd.length-1; i>0; i--) {
        const p=kd[i-1], c=kd[i];
        if(p.k != null && p.d != null && c.k != null && c.d != null) {
            if(p.k<=p.d && c.k>c.d) return {...c, type:'golden', txt:'黃金交叉'};
            if(p.k>=p.d && c.k<c.d) return {...c, type:'death', txt:'死亡交叉'};
        }
    } return null;
};

const getDeduction = (dailyData, latestClose, n) => {
    if (!dailyData || dailyData.length === 0) return { price: 0, diff: 0, isSafe: true, date: '--' };
    const idx = Math.max(0, dailyData.length - n);
    const target = dailyData[idx];
    return { date: target.date, price: target.close || 0, diff: latestClose - (target.close || 0), isSafe: latestClose >= (target.close || 0) };
};

onMounted(async () => {
    try {
        const res = await $fetch('/api/macrowave/taiex');
        if (!res || !res.success) throw new Error(res?.message || '資料獲取失敗');
        
        const safeDaily = sanitize(res.data.daily);
        if (safeDaily.length === 0) throw new Error('API 傳回的日線數據為空');

        taiexData.value = {
            daily: calcKD(safeDaily),
            weekly: calcKD(sanitize(res.data.weekly)),
            monthly: calcKD(sanitize(res.data.monthly))
        };
        
        const daily = taiexData.value.daily, latest = daily[daily.length-1].close || 0;
        const ma20 = calcMA(20, daily), ma60 = calcMA(60, daily);
        const lw = findCross(taiexData.value.weekly), lm = findCross(taiexData.value.monthly);

        const getVal = (arr) => arr && arr.length > 0 ? arr[arr.length-1] : {k:0, d:0};
        const getMa = (arr) => arr && arr.length > 0 ? arr[arr.length-1] || 0 : 0;
        const getPrevMa = (arr) => arr && arr.length > 1 ? arr[arr.length-2] || 0 : 0;

        analysis.value = {
            daily: {
                current: latest, ma20: getMa(ma20), ma60: getMa(ma60),
                ma20_trend: getMa(ma20) > getPrevMa(ma20) ? '<span class="text-danger">↗</span>' : '<span class="text-success">↘</span>',
                ma60_trend: getMa(ma60) > getPrevMa(ma60) ? '<span class="text-danger">↗</span>' : '<span class="text-success">↘</span>',
                deduction20: getDeduction(daily, latest, 20),
                deduction60: getDeduction(daily, latest, 60)
            },
            weekly: { 
                k: getVal(taiexData.value.weekly).k, d: getVal(taiexData.value.weekly).d,
                analysisTxt: lw ? `前次${lw.txt}於 ${lw.date}。變動 ${Math.round(Math.abs(latest-lw.close))} 點。` : '歷史數據不足',
                alertText: lw && Math.abs(latest-lw.close)>800 ? '⚠️ 超出傳統極值' : '✅ 尚有空間', 
                alertClass: lw && Math.abs(latest-lw.close)>800 ? 'alert-danger' : 'alert-success'
            },
            monthly: {
                k: getVal(taiexData.value.monthly).k, d: getVal(taiexData.value.monthly).d,
                analysisTxt: lm ? `前次${lm.txt}於 ${lm.date}。變動 ${Math.round(Math.abs(latest-lm.close))} 點。` : '歷史數據不足',
                alertText: lm && Math.abs(latest-lm.close)>2000 ? '⚠️ 長線達標' : '✅ 長線趨勢中', 
                alertClass: lm && Math.abs(latest-lm.close)>2000 ? 'alert-danger' : 'alert-success'
            }
        };

        let checkCount = 0;
        const checkEcharts = setInterval(() => {
            if (echarts) {
                clearInterval(checkEcharts);
                renderChart();
            } else if (checkCount > 50) {
                clearInterval(checkEcharts);
                errorMsg.value = 'ECharts 圖表庫載入失敗';
            }
            checkCount++;
        }, 200);

    } catch (err) {
        console.error(err);
        errorMsg.value = err.message || '資料解析發生錯誤';
    } finally {
        isLoading.value = false;
    }
});

function renderChart() {
    if(!taiexData.value) return;
    const data = taiexData.value[currentPeriod.value];
    if(!data || data.length === 0) return;

    const ma20 = calcMA(20, data), ma60 = calcMA(60, data);
    
    const kdMarks = [], candleMarks = [];
    for(let i=1; i<data.length; i++) {
        if(data[i-1].k!=null && data[i].k!=null) {
            if(data[i-1].k<=data[i-1].d && data[i].k>data[i].d) kdMarks.push({coord:[i, data[i].k], symbol:'arrow', symbolSize:12, itemStyle:{color:'#dc3545'}});
            if(data[i-1].k>=data[i-1].d && data[i].k<data[i].d) kdMarks.push({coord:[i, data[i].k], symbol:'arrow', symbolRotate:180, symbolSize:12, itemStyle:{color:'#198754'}});
        }
    }
    if(currentPeriod.value==='daily' && data.length>=60) {
        candleMarks.push({coord:[data.length-20, data[data.length-20].close], value:'20MA扣抵', symbol:'pin', symbolSize:40, itemStyle:{color:'#0dcaf0'}});
        candleMarks.push({coord:[data.length-60, data[data.length-60].close], value:'60MA扣抵', symbol:'pin', symbolSize:40, itemStyle:{color:'#ffc107'}});
    }

    const dom = document.getElementById('taiexChartTrad');
    if(!dom || !echarts) return;
    if(chartInstance) chartInstance.dispose();
    chartInstance = echarts.init(dom);
    
    chartInstance.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        axisPointer: { link: [{ xAxisIndex: 'all' }] },
        legend: { data: ['K線', '20MA', '60MA', '成交量', 'K值', 'D值'], top: 5 },
        grid: [{ left: '8%', right: '5%', top: '10%', height: '45%' }, { left: '8%', right: '5%', top: '60%', height: '12%' }, { left: '8%', right: '5%', top: '78%', height: '12%' }],
        xAxis: [{ type: 'category', data: data.map(i=>i.date), gridIndex: 0, axisLabel: { show: false } }, { type: 'category', data: data.map(i=>i.date), gridIndex: 1, axisLabel: { show: false } }, { type: 'category', data: data.map(i=>i.date), gridIndex: 2 }],
        yAxis: [{ scale: true, gridIndex: 0 }, { scale: true, gridIndex: 1, axisLabel: { show: false } }, { min: 0, max: 100, gridIndex: 2 }],
        dataZoom: [{ type: 'inside', xAxisIndex: [0, 1, 2], start: 70, end: 100 }, { show: true, xAxisIndex: [0, 1, 2], top: '94%', start: 70, end: 100 }],
        series: [
            { name: 'K線', type: 'candlestick', data: data.map(i=>[i.open, i.close, i.low, i.high]), itemStyle: { color: '#dc3545', color0: '#198754' }, markPoint: { data: candleMarks, label: {color:'#000', fontWeight:'bold'} } },
            { name: '20MA', type: 'line', data: ma20, smooth: true, symbol: 'none', lineStyle: { color: '#0dcaf0' } },
            { name: '60MA', type: 'line', data: ma60, smooth: true, symbol: 'none', lineStyle: { color: '#ffc107' } },
            { name: '成交量', type: 'bar', data: data.map(i=>({value:i.volume||0, itemStyle:{color:i.close>=i.open?'#dc3545':'#198754'}})), xAxisIndex: 1, yAxisIndex: 1 },
            { name: 'K值', type: 'line', data: data.map(i=>i.k), xAxisIndex: 2, yAxisIndex: 2, lineStyle: { color: '#dc3545' }, markPoint: { data: kdMarks, label:{show:false} } },
            { name: 'D值', type: 'line', data: data.map(i=>i.d), xAxisIndex: 2, yAxisIndex: 2, lineStyle: { color: '#0d6efd' } }
        ]
    });
}
</script>
