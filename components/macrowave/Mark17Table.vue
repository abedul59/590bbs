<template>
  <div class="col-12 mb-4">
      <div class="card shadow-sm border-0 mark17-card">
        <button
          type="button"
          class="card-header bg-dark text-white fw-bold d-flex justify-content-between align-items-center border-0 text-start"
          :aria-expanded="expanded"
          aria-controls="mark17Details"
          @click="expanded = !expanded"
        >
          <span>📋 Mark 17 詳細計分表（含原始數值與前值對照）</span>
          <small>{{ expanded ? '▼ 點擊收合' : '▶ 點擊展開' }}</small>
        </button>

        <div v-show="expanded" id="mark17Details" class="card-body p-0">
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
                <tr v-for="(item, index) in rows" :key="`${item.item}-${index}`">
                  <td class="fw-bold text-dark">{{ displayItem(item.item) }}</td>
                  <td class="text-center">
                    <div :class="['fw-bold fs-6 font-monospace', valueClass(item)]">{{ displayValue(item.value) }}</div>
                    <div v-if="item.prev_value !== undefined && item.prev_value !== null" class="text-muted mt-1 font-monospace previous-value">
                      （前值：{{ item.prev_value }}）
                    </div>
                  </td>
                  <td class="text-center">
                    <span v-if="displayScore(item.score) !== '-'" class="badge bg-danger rounded-pill px-3 fs-6">
                      {{ displayScore(item.score) }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
                <tr v-if="rows.length === 0">
                  <td colspan="3" class="text-center text-muted py-4">目前資料沒有 Mark 17 明細，請使用最新版 AutoSync EXE 重新上傳。</td>
                </tr>

                <tr class="table-warning border-top border-warning">
                  <td colspan="3" class="fw-bold text-center text-dark py-2 supplemental-title">以下為通膨重點監控數值補充</td>
                </tr>
                <tr>
                  <td class="fw-bold text-secondary">美國 CPI（消費者物價指數 YoY）</td>
                  <td class="text-center">
                    <div class="fw-bold text-dark fs-6 font-monospace">{{ rawIndicators.CPI ?? '--' }} %</div>
                    <div class="text-muted mt-1 font-monospace previous-value">（前值：{{ rawIndicators.CPI_Prev ?? '--' }} %）</div>
                  </td>
                  <td class="text-center text-muted">-</td>
                </tr>
                <tr>
                  <td class="fw-bold text-secondary">美國 PPI（生產者物價指數 YoY）</td>
                  <td class="text-center">
                    <div class="fw-bold text-dark fs-6 font-monospace">{{ rawIndicators.PPI ?? '--' }} %</div>
                    <div class="text-muted mt-1 font-monospace previous-value">（前值：{{ rawIndicators.PPI_Prev ?? '--' }} %）</div>
                  </td>
                  <td class="text-center text-muted">-</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  content: { type: Object, default: () => ({}) }
})

const expanded = ref(true)
const rawIndicators = computed(() => props.content?.raw_indicators || {})
const rows = computed(() => {
  const source = props.content?.mark17 || props.content?.mark17_details || []
  if (!Array.isArray(source)) return []
  return source.map((item) => {
    if (Array.isArray(item)) {
      return { item: item[0], value: item[1], score: item[2], status: '' }
    }
    return item && typeof item === 'object' ? item : { item: String(item), value: '--', score: '-' }
  })
})

const displayItem = (item) => String(item || '未命名項目').replace(/^(?:美國\s+)?PMI/, '美國 PMI')
const displayValue = (value) => value === undefined || value === null || value === '' ? '--' : value
const displayScore = (score) => {
  if (score === undefined || score === null || score === '' || score === '-') return '-'
  if (typeof score === 'number') return score > 0 ? `+${score}` : String(score)
  const text = String(score)
  const numeric = Number.parseFloat(text)
  if (Number.isFinite(numeric) && numeric > 0 && !text.startsWith('+')) return `+${text}`
  return text
}
const valueClass = (item) => {
  if (item.status === 'Unavailable' || String(item.value).includes('N/A')) return 'text-secondary'
  return Number.parseFloat(item.score) > 0 ? 'text-dark' : 'text-success'
}
</script>

<style scoped>
.mark17-card { overflow: hidden; }
.mark17-card .card-header { width: 100%; min-height: 2.7rem; }
.mark17-card th { white-space: nowrap; }
.previous-value { font-size: .75rem; }
.supplemental-title { font-size: .85rem; }
</style>
