<template>
  <div v-if="unlocked" class="private-tools-page">
    <nav class="private-tools-nav">
      <div class="private-tools-brand">🔐 隱藏工具後台</div>
      <div class="private-tools-actions">
        <button :class="{ active: selectedView === 'macrowave' }" @click="selectView('macrowave')">📊 MacroWave</button>
        <button :class="{ active: selectedView === 'eco4cycles' }" @click="selectView('eco4cycles')">🔄 Eco4Cycles</button>
        <button :class="{ active: selectedView === 'stock-dashboard' }" @click="selectView('stock-dashboard')">📈 六大指標與本益比</button>
        <button :class="{ active: selectedView === 'twstocktracker' }" @click="selectView('twstocktracker')">📊 台股資金流向</button>
        <button :class="{ active: selectedView === 'moneydam' }" @click="selectView('moneydam')">💧 六大水庫資金流向</button>
        <button v-if="selectedView" @click="showChooser">選擇工具</button>
        <button @click="returnToAdmin">返回後台</button>
        <button @click="returnHome">返回首頁</button>
      </div>
    </nav>

    <AdminMacrowave v-if="selectedView === 'macrowave'" @exit="returnToAdmin" @home="returnHome" />
    <section v-else-if="selectedView === 'eco4cycles'" class="eco4cycles-view">
      <header class="eco4cycles-title">
        <h1>🔄 Eco4Cycles 景氣循環儀表板</h1>
        <p>全球經濟週期判定、歷史紀錄與資產配置策略</p>
      </header>
      <Eco4cyclesDashboard />
    </section>
    <section v-else-if="selectedView === 'stock-dashboard'" class="stock-dashboard-view">
      <header class="stock-dashboard-title">
        <h1>📈 總大六大指標和本益比區間分析</h1>
        <p>台股六大基本面指標、EPS 試算與本益比價格區間</p>
      </header>
      <StockIndicatorDashboard />
    </section>
    <section v-else-if="selectedView === 'twstocktracker'" class="twstocktracker-view">
      <header class="twstocktracker-title">
        <h1>📊 台股資金流向儀表板</h1>
        <p>上市、上櫃、興櫃類股平均數據與成交額 Top 30</p>
      </header>
      <TwstocktrackerDashboard />
    </section>
    <section v-else-if="selectedView === 'moneydam'" class="moneydam-view">
      <MoneydamDashboard />
    </section>
    <section v-else class="tool-chooser">
      <div class="chooser-panel">
        <p class="chooser-kicker">PRIVATE CONSOLE</p>
        <h1>選擇要進入的總經工具</h1>
        <p>五個工具共用這個獨立頁面；網址會保留目前選擇，重新整理不會回到後台。</p>
        <div class="tool-grid">
          <button class="tool-card macrowave-card" @click="selectView('macrowave')">
            <span>📊</span><strong>MacroWave 總經戰情室</strong><small>台美市場、領先指標與風險監控</small>
          </button>
          <button class="tool-card cycles-card" @click="selectView('eco4cycles')">
            <span>🔄</span><strong>Eco4Cycles 景氣循環</strong><small>景氣四階段判定與歷史資料</small>
          </button>
          <button class="tool-card stock-dashboard-card" @click="selectView('stock-dashboard')">
            <span>📈</span><strong>總大六大指標和本益比區間分析</strong><small>六大指標、EPS 模擬與本益比價格區間</small>
          </button>
          <button class="tool-card twstocktracker-card" @click="selectView('twstocktracker')">
            <span>📊</span><strong>台股資金流向儀表板</strong><small>類股平均漲跌、成交量與成交額 Top 30</small>
          </button>
          <button class="tool-card moneydam-card" @click="selectView('moneydam')">
            <span>💧</span><strong>六大水庫資金流向分析</strong><small>外匯、債券、通膨、銀行與房地產資金流向</small>
          </button>
        </div>
      </div>
    </section>
  </div>

  <section v-else class="macrowave-login min-h-screen d-flex align-items-center justify-content-center p-4">
    <form class="card border-0 shadow-lg p-4 w-100" @submit.prevent="unlock">
      <h1 class="h4 fw-bold text-center mb-2">🔐 隱藏工具後台</h1>
      <p class="text-muted text-center mb-4">請輸入管理員密碼</p>
      <input v-model="password" type="password" autocomplete="current-password" class="form-control mb-2" autofocus>
      <p v-if="errorMessage" class="text-danger small fw-bold mb-2">{{ errorMessage }}</p>
      <button type="submit" class="btn btn-primary fw-bold w-100">進入工具後台</button>
      <NuxtLink to="/" class="btn btn-link text-secondary mt-2">返回首頁</NuxtLink>
    </form>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { getTodayPassword } from '@/utils/auth'
import StockIndicatorDashboard from '@/components/stock-dashboard/Dashboard.vue'
import TwstocktrackerDashboard from '@/components/twstocktracker/Dashboard.vue'
import MoneydamDashboard from '@/components/moneydam/Dashboard.vue'

useHead({
  title: '隱藏總經工具後台',
  link: [{ rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' }],
  script: [{ src: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js', defer: true }]
})

const route = useRoute()
const macrowaveMode = useState('macrowaveMode', () => false)
const unlocked = ref(false)
const password = ref('')
const errorMessage = ref('')
const selectedView = computed(() => ['macrowave', 'eco4cycles', 'stock-dashboard', 'twstocktracker', 'moneydam'].includes(String(route.query.view)) ? String(route.query.view) : '')

macrowaveMode.value = true

onMounted(() => {
  unlocked.value = sessionStorage.getItem('macrowave_unlocked') === '1'
})

const unlock = () => {
  if (password.value !== getTodayPassword()) {
    errorMessage.value = '密碼錯誤'
    return
  }
  sessionStorage.setItem('macrowave_unlocked', '1')
  unlocked.value = true
  password.value = ''
  errorMessage.value = ''
}

const selectView = view => navigateTo({ path: '/macrowave', query: { view } })
const showChooser = () => navigateTo('/macrowave')
const returnToAdmin = () => navigateTo('/admin')
const returnHome = () => navigateTo('/')

onBeforeUnmount(() => {
  macrowaveMode.value = false
})
</script>

<style scoped>
.private-tools-page { min-height: 100vh; background: #f4f6f9; }
.private-tools-nav { position: sticky; top: 0; z-index: 1080; display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: .7rem 1rem; color: #fff; background: #111827; box-shadow: 0 3px 12px #0003; }
.private-tools-brand { font-weight: 800; white-space: nowrap; }
.private-tools-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: .5rem; }
.private-tools-actions button { border: 1px solid #ffffff3d; border-radius: .55rem; padding: .45rem .75rem; color: #e5e7eb; background: #1f2937; font-weight: 700; }
.private-tools-actions button:hover, .private-tools-actions button.active { color: #fff; background: #2563eb; }
.tool-chooser { min-height: calc(100vh - 62px); display: grid; place-items: center; padding: 2rem; background: linear-gradient(135deg, #172554, #164e63); }
.chooser-panel { width: min(900px, 100%); padding: clamp(1.5rem, 5vw, 3.5rem); border-radius: 1.5rem; color: #fff; background: #ffffff12; border: 1px solid #ffffff30; box-shadow: 0 25px 70px #0004; backdrop-filter: blur(12px); }
.chooser-panel h1 { margin-bottom: .75rem; font-weight: 900; }
.chooser-kicker { letter-spacing: .18em; color: #67e8f9; font-size: .78rem; font-weight: 800; }
.tool-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; margin-top: 2rem; }
.tool-card { min-height: 210px; display: flex; flex-direction: column; align-items: flex-start; justify-content: center; gap: .7rem; padding: 1.5rem; border: 0; border-radius: 1.2rem; color: #fff; text-align: left; transition: transform .2s ease, box-shadow .2s ease; }
.tool-card:hover { transform: translateY(-5px); box-shadow: 0 18px 35px #0004; }
.tool-card span { font-size: 2.6rem; }
.tool-card strong { font-size: 1.25rem; }
.tool-card small { opacity: .86; }
.macrowave-card { background: linear-gradient(135deg, #2563eb, #0891b2); }
.cycles-card { background: linear-gradient(135deg, #059669, #0f766e); }
.stock-dashboard-card { background: linear-gradient(135deg, #7c3aed, #db2777); }
.twstocktracker-card { background: linear-gradient(135deg, #ea580c, #dc2626); }
.moneydam-card { background: linear-gradient(135deg, #059669, #0f766e); }
.eco4cycles-view { min-height: calc(100vh - 62px); padding-bottom: 2rem; background: #f8f9fa; }
.eco4cycles-title { padding: 2rem 1rem; color: #fff; text-align: center; background: linear-gradient(135deg, #065f46, #0f766e); }
.eco4cycles-title h1 { margin: 0 0 .35rem; font-weight: 900; }
.eco4cycles-title p { margin: 0; opacity: .88; }
.stock-dashboard-view { min-height: calc(100vh - 62px); padding-bottom: 2rem; background: #f8f9fa; }
.stock-dashboard-title { padding: 2rem 1rem; color: #fff; text-align: center; background: linear-gradient(135deg, #4c1d95, #be185d); }
.stock-dashboard-title h1 { margin: 0 0 .35rem; font-weight: 900; }
.stock-dashboard-title p { margin: 0; opacity: .88; }
.twstocktracker-view { min-height: calc(100vh - 62px); background: #f8fafc; }
.twstocktracker-title { padding: 2rem 1rem; color: #fff; text-align: center; background: linear-gradient(135deg, #c2410c, #b91c1c); }
.twstocktracker-title h1 { margin: 0 0 .35rem; font-weight: 900; }
.twstocktracker-title p { margin: 0; opacity: .88; }
.moneydam-view { min-height: calc(100vh - 62px); }
.macrowave-login { background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 100%); }
.macrowave-login .card { max-width: 26rem; }
@media (max-width: 700px) {
  .private-tools-nav { align-items: flex-start; flex-direction: column; }
  .private-tools-actions { justify-content: flex-start; }
  .tool-grid { grid-template-columns: 1fr; }
}
</style>
