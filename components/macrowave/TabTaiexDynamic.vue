<template>
  <div class="container pb-5 mt-4">
    
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <h4 class="fw-bold mb-0 text-secondary" style="font-size: 1.25rem;"></h4>
        <a href="https://drive.google.com/drive/folders/1NM0lB14yK3iEv_HclNKyVgda8AdT6IOy?usp=sharing" 
           target="_blank" rel="noopener noreferrer" 
           class="btn btn-info fw-bold shadow-sm text-dark">
           📁 觀看 Evacarry 資料
        </a>
    </div>

    <div class="card shadow-sm border-0 mb-4 bg-light">
      <div class="card-header bg-success text-white py-2 d-flex justify-content-between align-items-center">
        <h6 class="fw-bold mb-0">📌 專屬佈告欄筆記 (雲端同步)</h6>
        <button class="btn btn-light btn-sm fw-bold text-success" @click="openBulletinModal" v-if="!showBulletinForm">
          ➕ 新增筆記
        </button>
      </div>
      
      <div class="card-body" v-if="showBulletinForm">
        <div class="bg-white p-3 rounded shadow-sm border border-success">
          <div class="mb-2">
            <label class="form-label fw-bold small text-muted mb-1">標題</label>
            <input type="text" class="form-control form-control-sm" v-model="formBulletin.title" placeholder="輸入筆記標題">
          </div>
          <div class="mb-2">
            <label class="form-label fw-bold small text-muted mb-1">內容</label>
            <textarea class="form-control form-control-sm" rows="3" v-model="formBulletin.content" placeholder="輸入筆記內容..."></textarea>
          </div>
          <div class="mb-3">
            <label class="form-label fw-bold small text-muted mb-1">網址連結 (複數網址請按 Enter 換行輸入)</label>
            <textarea class="form-control form-control-sm" rows="2" v-model="formBulletin.urlsText" placeholder="https://..."></textarea>
          </div>
          <div class="text-end">
            <button class="btn btn-outline-secondary btn-sm me-2 fw-bold" @click="showBulletinForm = false" :disabled="isSaving">取消</button>
            <button class="btn btn-success btn-sm fw-bold" @click="saveBulletin" :disabled="isSaving">
              <span v-if="isSaving" class="spinner-border spinner-border-sm me-1"></span>💾 儲存
            </button>
          </div>
        </div>
      </div>

      <div class="card-body" v-else>
        <div class="row g-3">
          <div class="col-md-6 col-lg-4" v-for="item in bulletins" :key="item.id">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-3 d-flex flex-column">
                <h6 class="fw-bold text-dark border-bottom pb-2 mb-2">{{ item.title }}</h6>
                <p class="text-muted small mb-3" style="white-space: pre-wrap; font-size: 0.85rem; flex-grow: 1;">{{ item.content }}</p>
                <div v-if="item.urls && item.urls.length > 0" class="d-flex flex-column gap-1 mb-2">
                  <a v-for="(url, idx) in item.urls" :key="idx" :href="url" target="_blank" class="badge bg-primary text-decoration-none text-start text-truncate py-2 px-2" style="max-width: 100%;">
                    🔗 {{ url }}
                  </a>
                </div>
              </div>
              <div class="card-footer bg-white border-top-0 pt-0 text-end">
                <button class="btn btn-light btn-sm text-primary fw-bold me-2 px-2 py-0" @click="editBulletin(item)">編輯</button>
                <button class="btn btn-light btn-sm text-danger fw-bold px-2 py-0" @click="deleteBulletin(item.id)">刪除</button>
              </div>
            </div>
          </div>
          <div v-if="bulletins.length === 0" class="col-12 text-center text-muted small py-3">
            目前無任何佈告筆記，請點擊右上方按鈕新增。
          </div>
        </div>
      </div>
    </div>

    <div v-if="errorMsg" class="alert alert-danger text-center shadow-sm fw-bold my-4">
        ❌ 系統錯誤：{{ errorMsg }}
    </div>

    <div class="card shadow-sm border-0 mb-4 overflow-hidden">
      <div class="card-header bg-primary text-white py-3">
        <h5 class="fw-bold mb-0">📜 台股十年週期理論 (加權指數規律修訂版)</h5>
      </div>
      <div class="card-body bg-light">
        <div class="row align-items-center">
          <div class="col-lg-5">
            <div class="small p-3 bg-white rounded border" style="line-height: 1.7; color: #444;">
              <p class="mb-2"><strong>1. 結構與規律：</strong> 每一次的十年週期約 120 個月，內含大多頭與空頭修正波。根據西元年規律，<strong>尾數 2, 5, 8 年的年底為多頭起漲點；尾數 7, 0 年的年中為空頭起跌點</strong>。</p>
              <p class="mb-2"><strong>2. 週期多空細解：</strong> 十年中包含明顯的上升浪與 A-B-C 下跌調整。把握這幾個關鍵西元年尾數，就能抓到長波段的最佳轉換時機。</p>
              <p class="mb-0"><strong>3. KD 極值對應：</strong> 月KD交叉定波段 (十年內約6-8次交叉，極值約 25%)。週KD每年交叉 6~8 次 (存續約2個月，極值約 7.5%~10%)。</p>
            </div>
          </div>
          <div class="col-lg-7 mt-3 mt-lg-0">
            <div id="theoryDiagram" style="width: 100%; height: 230px;"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="row mb-4" v-if="analysis">
      
      <div class="col-md-6 mb-3">
          <div class="card h-100 border-danger shadow-sm">
              <div class="card-header bg-danger text-white fw-bold d-flex justify-content-between align-items-center">
                  <span>🚀 長線動態極值 (25%)</span>
                  <span :class="['badge', analysis.monthly.crossCount >= 6 ? 'bg-danger text-white border border-white' : 'bg-white text-danger']">
                      近10年月KD交叉: {{ analysis.monthly.crossCount }} 次
                  </span>
              </div>
              <div class="card-body d-flex flex-column">
                  <div class="d-flex justify-content-between mb-2"><span class="text-muted">最新月 KD</span><span class="fw-bold fs-5">K: <span :class="analysis.monthly.k > 80 ? 'text-danger' : ''">{{ analysis.monthly.k.toFixed(2) }}</span> / D: {{ analysis.monthly.d.toFixed(2) }}</span></div>
                  <div class="d-flex justify-content-between mb-3"><span class="text-muted">季線 (60MA) 狀態</span><span class="fw-bold fs-5">{{ analysis.daily.ma60.toFixed(2) }} <span v-html="analysis.daily.ma60_trend"></span></span></div>

                  <div class="bg-light p-3 rounded border border-danger mb-3">
                      <div class="fw-bold text-danger mb-2 border-bottom border-danger pb-1">🎯 25% 動態極值追蹤</div>
                      <div v-if="analysis.monthly.basePrice > 0">
                          <div class="d-flex justify-content-between small mb-1"><span>前次轉折日期</span><span>{{ analysis.monthly.baseDate }}</span></div>
                          <div class="d-flex justify-content-between small mb-1"><span>轉折類型</span><span :class="analysis.monthly.type === 'golden' ? 'text-danger fw-bold' : 'text-success fw-bold'">{{ analysis.monthly.crossType }}</span></div>
                          <div class="d-flex justify-content-between mb-1"><span>基準點位</span><span class="fw-bold">{{ analysis.monthly.basePrice.toFixed(0) }} 點</span></div>
                          <div class="d-flex justify-content-between mb-1"><span>動態極值目標</span><span class="fw-bold text-dark">{{ analysis.monthly.targetPrice.toFixed(0) }} 點</span></div>
                          <div class="mt-2 pt-2 border-top d-flex justify-content-between align-items-center">
                              <span class="small fw-bold">波段推進進度：</span><span class="badge bg-danger fs-6">{{ analysis.monthly.currentDiff.toFixed(0) }} 點 ({{ analysis.monthly.percentDiff.toFixed(1) }}%)</span>
                          </div>
                      </div>
                      <div v-else class="text-center text-muted py-3">歷史數據不足</div>
                  </div>

                  <div class="bg-white p-2 rounded border mb-3 small shadow-sm">
                      <div class="d-flex justify-content-between mb-1"><span class="text-muted">季線(60MA) 防守價</span><span class="fw-bold text-dark">{{ analysis.daily.deduction60.price.toFixed(0) }}</span></div>
                      <div class="d-flex justify-content-between"><span>防禦狀態</span>
                          <span v-if="analysis.daily.deduction60.isSafe" class="text-success fw-bold">安全 (+{{ analysis.daily.deduction60.diff.toFixed(0) }})</span>
                          <span v-else class="text-danger fw-bold">跌破 ({{ analysis.daily.deduction60.diff.toFixed(0) }})</span>
                      </div>
                  </div>
                  
                  <div v-if="analysis.monthly.crossCount >= 6" class="alert alert-secondary py-1 mb-2 text-center small fw-bold">💡 提示：近10年交叉達 {{ analysis.monthly.crossCount }} 次，請配合均線判斷真假轉折</div>
                  <hr class="mt-auto">
                  <div class="alert mb-0 py-2 fw-bold text-center" :class="analysis.monthly.alertClass">{{ analysis.monthly.alertText }}</div>
              </div>
          </div>
      </div>

      <div class="col-md-6 mb-3">
          <div class="card h-100 border-warning shadow-sm">
              <div class="card-header bg-warning text-dark fw-bold d-flex justify-content-between align-items-center">
                  <span>🚀 中線動態極值 (10%)</span>
                  <span :class="['badge', analysis.weekly.crossCount > 8 ? 'bg-danger text-white' : 'bg-dark text-white']">今年週 KD: {{ analysis.weekly.crossCount }} 次</span>
              </div>
              <div class="card-body d-flex flex-column">
                  <div class="d-flex justify-content-between mb-2"><span class="text-muted">最新週 KD</span><span class="fw-bold fs-5">K: <span :class="analysis.weekly.k > 80 ? 'text-danger' : ''">{{ analysis.weekly.k.toFixed(2) }}</span> / D: {{ analysis.weekly.d.toFixed(2) }}</span></div>
                  <div class="d-flex justify-content-between mb-3"><span class="text-muted">月線 (20MA) 狀態</span><span class="fw-bold fs-5">{{ analysis.daily.ma20.toFixed(2) }} <span v-html="analysis.daily.ma20_trend"></span></span></div>

                  <div class="bg-light p-3 rounded border border-warning mb-3">
                      <div class="fw-bold text-dark mb-2 border-bottom border-warning pb-1">🎯 10% 動態極值追蹤</div>
                      <div v-if="analysis.weekly.basePrice > 0">
                          <div class="d-flex justify-content-between small mb-1"><span>前次轉折日期</span><span>{{ analysis.weekly.baseDate }}</span></div>
                          <div class="d-flex justify-content-between small mb-1"><span>轉折類型</span><span :class="analysis.weekly.type === 'golden' ? 'text-danger fw-bold' : 'text-success fw-bold'">{{ analysis.weekly.crossType }}</span></div>
                          <div class="d-flex justify-content-between mb-1"><span>基準點位</span><span class="fw-bold">{{ analysis.weekly.basePrice.toFixed(0) }} 點</span></div>
                          <div class="d-flex justify-content-between mb-1"><span>極值區間</span><span class="fw-bold text-dark">{{ analysis.weekly.targetMin.toFixed(0) }} ~ {{ analysis.weekly.targetMax.toFixed(0) }} 點</span></div>
                          <div class="mt-2 pt-2 border-top d-flex justify-content-between align-items-center">
                              <span class="small fw-bold">波段推進進度：</span><span class="badge bg-warning text-dark fs-6">{{ analysis.weekly.currentDiff.toFixed(0) }} 點 ({{ analysis.weekly.percentDiff.toFixed(1) }}%)</span>
                          </div>
                      </div>
                      <div v-else class="text-center text-muted py-3">歷史數據不足</div>
                  </div>

                  <div class="bg-white p-2 rounded border mb-3 small shadow-sm">
                      <div class="d-flex justify-content-between mb-1"><span class="text-muted">月線(20MA) 防守價</span><span class="fw-bold text-dark">{{ analysis.daily.deduction20.price.toFixed(0) }}</span></div>
                      <div class="d-flex justify-content-between"><span>防禦狀態</span>
                          <span v-if="analysis.daily.deduction20.isSafe" class="text-success fw-bold">安全 (+{{ analysis.daily.deduction20.diff.toFixed(0) }})</span>
                          <span v-else class="text-danger fw-bold">跌破 ({{ analysis.daily.deduction20.diff.toFixed(0) }})</span>
                      </div>
                  </div>

                  <div v-if="analysis.weekly.crossCount > 8" class="alert alert-danger py-1 mb-2 text-center small fw-bold">⚠️ 注意：今年交叉頻率過高，波動劇烈</div>
                  <hr class="mt-auto">
                  <div class="alert mb-0 py-2 fw-bold text-center" :class="analysis.weekly.alertClass">{{ analysis.weekly.alertText }}</div>
              </div>
          </div>
      </div>
    </div>

    <div v-if="isLoading && !errorMsg" class="text-center my-5">
      <div class="spinner-border text-danger"></div><p class="mt-2 fw-bold">動態極值運算中...</p>
    </div>

    <div class="card shadow-sm mb-4" v-show="!isLoading && taiexData && !errorMsg">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap">
          <h5 class="fw-bold text-secondary mb-0">台股加權指數 - 動態極值對照圖</h5>
          <div class="btn-group mt-2 mt-md-0">
            <button v-for="p in ['daily', 'weekly', 'monthly']" :key="p" @click="currentPeriod = p; renderChart()" :class="['btn fw-bold px-4', currentPeriod === p ? 'btn-danger' : 'btn-outline-danger']">{{ p === 'daily' ? '日 K' : p === 'weekly' ? '週 K' : '月 K' }}</button>
          </div>
        </div>
        <div id="taiexChartDyn" style="width: 100%; height: 75vh; min-height: 550px;"></div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

// =====================================
// 佈告欄筆記功能邏輯 (API 資料庫版)
// =====================================
const bulletins = ref([]);
const showBulletinForm = ref(false);
const isEditing = ref(false);
const formBulletin = ref({ id: null, title: '', content: '', urlsText: '' });
const isSaving = ref(false);

const loadBulletins = async () => {
    try {
        const res = await $fetch('/api/macrowave/bulletins');
        if (res && res.success) {
            bulletins.value = res.data;
        }
    } catch (e) {
        console.error('讀取佈告欄失敗', e);
    }
};

const openBulletinModal = () => {
    isEditing.value = false;
    formBulletin.value = { id: null, title: '', content: '', urlsText: '' };
    showBulletinForm.value = true;
};

const editBulletin = (item) => {
    isEditing.value = true;
    formBulletin.value = { 
        id: item.id, 
        title: item.title, 
        content: item.content, 
        urlsText: item.urls ? item.urls.join('\n') : '' 
    };
    showBulletinForm.value = true;
};

const saveBulletin = async () => {
    if (!formBulletin.value.title) {
        alert('筆記標題為必填項目！'); return;
    }
    isSaving.value = true;
    const urls = formBulletin.value.urlsText.split('\n').map(u => u.trim()).filter(u => u !== '');
    const payload = {
        id: formBulletin.value.id, 
        title: formBulletin.value.title, 
        content: formBulletin.value.content, 
        urls: urls
    };

    try {
        const res = await $fetch('/api/macrowave/bulletins', {
            method: 'POST',
            body: payload
        });
        if (res.success) {
            await loadBulletins();
            showBulletinForm.value = false;
        } else {
            alert('儲存失敗：' + res.message);
        }
    } catch (e) {
        alert('儲存發生錯誤，請確定已建立 bulletins 資料表及 API。');
    } finally {
        isSaving.value = false;
    }
};

const deleteBulletin = async (id) => {
    if(!confirm('確定要刪除這則筆記嗎？')) return;
    try {
        const res = await $fetch(`/api/macrowave/bulletins?id=${id}`, { method: 'DELETE' });
        if (res.success) {
            bulletins.value = bulletins.value.filter(b => b.id !== id);
        } else {
            alert('刪除失敗：' + res.message);
        }
    } catch (e) {
        alert('刪除發生錯誤');
    }
};

// =====================================
// 台股指標核心邏輯
// =====================================
const isLoading = ref(true);
const errorMsg = ref('');
const taiexData = ref(null);
const analysis = ref(null);
const currentPeriod = ref('daily');
let chartInstance = null;
let theoryChartInstance = null;

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
            if(p.k<=p.d && c.k>c.d) return {...c, type:'golden', crossType:'黃金交叉 (偏多)'};
            if(p.k>=p.d && c.k<c.d) return {...c, type:'death', crossType:'死亡交叉 (偏空)'};
        }
    } return null;
};

const countCross = (kd, periodStr) => {
    if (!kd || kd.length < 2) return 0;
    let cnt = 0;
    const currentYr = new Date().getFullYear();
    const tenYrsAgo = currentYr - 10;
    
    for(let i=1; i<kd.length; i++) {
        const p=kd[i-1], c=kd[i];
        if(p.k == null || p.d == null || c.k == null || c.d == null) continue;
        const dYr = new Date(c.date).getFullYear();
        
        if(periodStr === 'year' && dYr !== currentYr) continue;
        if(periodStr === 'decade' && dYr < tenYrsAgo) continue;
        
        if((p.k<=p.d && c.k>c.d) || (p.k>=p.d && c.k<c.d)) cnt++;
    } return cnt;
};

const getDeduction = (dailyData, latestClose, n) => {
    if (!dailyData || dailyData.length === 0) return { price: 0, diff: 0, isSafe: true, date: '--' };
    const idx = Math.max(0, dailyData.length - n);
    const target = dailyData[idx];
    return { date: target.date, price: target.close || 0, diff: latestClose - (target.close || 0), isSafe: latestClose >= (target.close || 0) };
};

onMounted(async () => {
    // 載入佈告欄資料庫資料
    await loadBulletins();

    try {
        const res = await $fetch('/api/macrowave/taiex');
        if (!res || !res.success) throw new Error(res?.message || '資料獲取失敗');
        
        const safeDaily = sanitize(res.data.daily);
        if (safeDaily.length === 0) throw new Error('API 傳回的日線數據為空，請稍後再試。');

        taiexData.value = {
            daily: calcKD(safeDaily),
            weekly: calcKD(sanitize(res.data.weekly)),
            monthly: calcKD(sanitize(res.data.monthly))
        };
        
        const daily = taiexData.value.daily, latest = daily[daily.length-1].close || 0;
        const ma20 = calcMA(20, daily), ma60 = calcMA(60, daily);
        
        const lw = findCross(taiexData.value.weekly);
        const lm = findCross(taiexData.value.monthly);

        const getPct = (wave) => wave ? (Math.abs(latest - wave.close) / wave.close) * 100 : 0;
        const getDiff = (wave) => wave ? (wave.type === 'golden' ? latest - wave.close : wave.close - latest) : 0;
        const getVal = (arr) => arr && arr.length > 0 ? arr[arr.length-1] : {k:0, d:0};
        const getMa = (arr) => arr && arr.length > 0 ? arr[arr.length-1] || 0 : 0;
        const getPrevMa = (arr) => arr && arr.length > 1 ? arr[arr.length-2] || 0 : 0;

        analysis.value = {
            daily: {
                current: latest, ma20: getMa(ma20), ma60: getMa(ma60),
                ma20_trend: getMa(ma20) > getPrevMa(ma20) ? '<span class="text-danger">↗ (上揚)</span>' : '<span class="text-success">↘ (下彎)</span>',
                ma60_trend: getMa(ma60) > getPrevMa(ma60) ? '<span class="text-danger">↗ (上揚)</span>' : '<span class="text-success">↘ (下彎)</span>',
                deduction20: getDeduction(daily, latest, 20),
                deduction60: getDeduction(daily, latest, 60)
            },
            weekly: { 
                k: getVal(taiexData.value.weekly).k, d: getVal(taiexData.value.weekly).d,
                basePrice: lw?.close||0, baseDate: lw?.date||'--', type: lw?.type||'', crossType: lw?.crossType||'--',
                currentDiff: Math.abs(getDiff(lw)), percentDiff: getPct(lw),
                targetMin: lw ? lw.close * (lw.type==='golden'?1.075:0.925) : 0,
                targetMax: lw ? lw.close * (lw.type==='golden'?1.1:0.9) : 0,
                crossCount: countCross(taiexData.value.weekly, 'year'),
                alertText: lw && getPct(lw) > 10 ? '⚠️ 嚴重警戒！突破 10% 動態極值' : '✅ 順勢推進中，空間未滿',
                alertClass: lw && getPct(lw) > 10 ? 'alert-danger' : 'alert-success'
            },
            monthly: {
                k: getVal(taiexData.value.monthly).k, d: getVal(taiexData.value.monthly).d,
                basePrice: lm?.close||0, baseDate: lm?.date||'--', type: lm?.type||'', crossType: lm?.crossType||'--',
                currentDiff: Math.abs(getDiff(lm)), percentDiff: getPct(lm),
                targetPrice: lm ? lm.close * (lm.type==='golden'?1.25:0.75) : 0,
                crossCount: countCross(taiexData.value.monthly, 'decade'),
                alertText: lm && getPct(lm) > 25 ? '⚠️ 突破 25% 長波動態極值' : '✅ 長線動態空間未滿',
                alertClass: lm && getPct(lm) > 25 ? 'alert-danger' : 'alert-success'
            }
        };

        nextTick(() => {
            let checkCount = 0;
            const checkEcharts = setInterval(() => {
                if (echarts) {
                    clearInterval(checkEcharts);
                    drawTheoryDiagram();
                    renderChart();
                } else if (checkCount > 50) { // 10秒超時
                    clearInterval(checkEcharts);
                    errorMsg.value = '圖表庫 (ECharts) 載入失敗，請檢查網路連線。';
                }
                checkCount++;
            }, 200);
        });

    } catch (err) {
        errorMsg.value = err.message || '資料解析發生未知的錯誤';
        console.error(err);
    } finally {
        isLoading.value = false;
    }
});

function drawTheoryDiagram() {
    const dom = document.getElementById('theoryDiagram');
    if(!dom || !echarts) return;
    
    if (theoryChartInstance) theoryChartInstance.dispose();
    theoryChartInstance = echarts.init(dom);
    
    theoryChartInstance.setOption({
        grid: { top: 35, bottom: 25, left: 30, right: 30 },
        tooltip: { trigger: 'axis', formatter: '{b}' },
        xAxis: { 
            type: 'category', 
            data: ['尾數 2\n年底起漲', '過渡波', '尾數 5\n年底起漲', '尾數 7\n年中起跌', '尾數 8\n年底起漲', '尾數 0\n年中起跌', '空頭落底', '尾數 2\n年底起漲'], 
            axisLine: { show: true, lineStyle: { color: '#ccc' } }, 
            axisLabel: { fontSize: 11, interval: 0, fontWeight: 'bold', color: '#555' } 
        },
        yAxis: { show: false, min: 0, max: 110 },
        series: [{
            type: 'line', smooth: true, symbolSize: 6, lineStyle: { width: 3, color: '#0d6efd' },
            data: [20, 60, 40, 90, 60, 100, 30, 20],
            markPoint: { 
                symbolSize: 45,
                data: [
                    { name: '起漲', coord: [0, 20], itemStyle: {color: '#dc3545'}, value: '起漲', label: {color: '#fff', fontSize: 10} }, 
                    { name: '起漲', coord: [2, 40], itemStyle: {color: '#dc3545'}, value: '起漲', label: {color: '#fff', fontSize: 10} }, 
                    { name: '起跌', coord: [3, 90], itemStyle: {color: '#198754'}, value: '起跌', label: {color: '#fff', fontSize: 10} },
                    { name: '起漲', coord: [4, 60], itemStyle: {color: '#dc3545'}, value: '起漲', label: {color: '#fff', fontSize: 10} },
                    { name: '起跌', coord: [5, 100], itemStyle: {color: '#198754'}, value: '起跌', label: {color: '#fff', fontSize: 10} },
                    { name: '次循環', coord: [7, 20], itemStyle: {color: '#dc3545'}, value: '次循環', label: {color: '#fff', fontSize: 10} }
                ] 
            }
        }]
    });
}

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

    const dom = document.getElementById('taiexChartDyn');
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
