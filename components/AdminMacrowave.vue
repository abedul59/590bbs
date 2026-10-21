<template>
  <section class="macrowave-viewport">
    <div class="macrowave-shell">
      <div class="header-section text-center position-relative">
        <button type="button" class="btn btn-sm btn-light exit-button" @click="$emit('exit')">返回後台</button>
        <h1 class="fw-bold">📊 MacroWave 總經戰情室</h1>
        <p class="opacity-90 mb-0">全方位總體經濟與資產配置監控中心</p>
      </div>

      <div class="container-fluid px-3 px-lg-4 mb-4">
        <ul class="nav nav-tabs nav-fill fw-bold fs-6 shadow-sm bg-white rounded-top flex-column flex-md-row">
          <li v-for="tab in tabs" :key="tab.id" class="nav-item">
            <button :class="['nav-link py-3 w-100', tab.className, { active: activeTab === tab.id }]" @click="activeTab = tab.id">
              {{ tab.label }}
            </button>
          </li>
        </ul>
      </div>

      <div class="tab-content px-2 px-lg-3">
        <KeepAlive>
          <component :is="currentTabComponent" />
        </KeepAlive>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import MacrowaveStockChart from './macrowave/StockChart.vue'
import MacrowaveDashboard from './macrowave/TabDashboard.vue'
import MacrowaveLeadIndicator from './macrowave/TabLeadIndicator.vue'
import MacrowaveOptionsChain from './macrowave/TabOptionsChain.vue'
import MacrowaveOptionsJournal from './macrowave/TabOptionsJournal.vue'
import MacrowaveTaiexDynamic from './macrowave/TabTaiexDynamic.vue'
import MacrowaveTaiexHistory from './macrowave/TabTaiexHistory.vue'
import MacrowaveTaiexHistoryMonthly from './macrowave/TabTaiexHistoryMonthly.vue'
import MacrowaveTaiexTraditional from './macrowave/TabTaiexTraditional.vue'
import MacrowaveTmfRetailRatio from './macrowave/TabTmfRetailRatio.vue'

defineEmits(['exit'])

useHead({
  link: [{ rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' }]
})

const tabs = [
  { id: 'macro', label: '🌍 總經戰情' },
  { id: 'taiex', label: '📈 傳統極值' },
  { id: 'dynamic', label: '🚀 動態極值與十年週期' },
  { id: 'history', label: '⏳ 週KD 歷史回測', className: 'text-success' },
  { id: 'historyMonthly', label: '⏳ 月KD 歷史回測', className: 'text-danger' },
  { id: 'tmf', label: '🔥 散戶多空比 (00631L)', className: 'text-primary' },
  { id: 'lead', label: '🔥 領先指標 (0050)', className: 'text-primary' },
  { id: 'usstock', label: '🇺🇸 美股 K 線查詢', className: 'text-warning text-darken' },
  { id: 'options', label: '🇺🇸 選擇權籌碼', className: 'text-info text-darken' },
  { id: 'journal', label: '📓 選擇權日誌', className: 'text-secondary text-darken' }
]

const components = {
  macro: MacrowaveDashboard,
  taiex: MacrowaveTaiexTraditional,
  dynamic: MacrowaveTaiexDynamic,
  history: MacrowaveTaiexHistory,
  historyMonthly: MacrowaveTaiexHistoryMonthly,
  tmf: MacrowaveTmfRetailRatio,
  lead: MacrowaveLeadIndicator,
  usstock: MacrowaveStockChart,
  options: MacrowaveOptionsChain,
  journal: MacrowaveOptionsJournal
}

const activeTab = ref('macro')
const currentTabComponent = computed(() => components[activeTab.value] || MacrowaveDashboard)
</script>

<style scoped>
.macrowave-viewport {
  position: relative;
  left: 50%;
  width: calc(100vw - 1rem);
  margin-left: calc(-50vw + .5rem);
  min-height: 80vh;
  color: #333;
  background: #f4f6f9;
  font-family: "Segoe UI", Roboto, sans-serif;
}
.macrowave-shell { min-height: 80vh; padding-bottom: 2rem; }
.header-section {
  margin-bottom: 1.5rem;
  padding: 2.25rem 5rem;
  color: white;
  background: linear-gradient(135deg, #1a2980 0%, #26d0ce 100%);
}
.exit-button { position: absolute; top: 1rem; left: 1rem; }
.nav-item { min-width: 10rem; flex: 1 1 10rem; }
.nav-tabs .nav-link { border: 0; color: #6c757d; transition: all .3s; background: transparent; }
.nav-tabs .nav-link.active { color: #0d6efd; border-bottom: 4px solid #0d6efd; }
.text-darken { filter: brightness(.85); font-weight: 700; }
@media (max-width: 640px) {
  .header-section { padding: 4rem 1rem 2rem; }
}
</style>
