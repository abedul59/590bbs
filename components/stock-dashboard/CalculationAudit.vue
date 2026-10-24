<template>
  <div class="calculation-audit mt-4">
    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-2">
      <h6 class="mb-0 fw-bold text-dark">🧾 推算過程與原始資料核對</h6>
      <small class="text-muted">公式 → 本次代入 → 結果 → 原始來源</small>
    </div>
    <div class="table-responsive">
      <table class="table table-sm table-bordered align-middle mb-0 audit-table">
        <thead class="table-light">
          <tr><th>數據</th><th>公式</th><th>本次代入與結果</th><th>爬蟲原始資料</th></tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in items" :key="`${item.label}-${index}`">
            <td class="fw-bold text-nowrap">{{ item.label }}</td>
            <td><code>{{ item.formula }}</code></td>
            <td>
              <div>{{ item.substitution || '-' }}</div>
              <div v-if="item.result !== undefined && item.result !== ''" class="fw-bold text-primary mt-1">＝ {{ item.result }}</div>
              <small v-if="item.note" class="d-block text-muted mt-1">{{ item.note }}</small>
            </td>
            <td>
              <a
                v-for="source in item.sources || []"
                :key="source.url"
                :href="source.url"
                target="_blank"
                rel="noopener noreferrer"
                class="d-block text-decoration-none mb-1"
              >🔗 {{ source.label }} ↗</a>
              <span v-if="!item.sources?.length" class="text-muted">由上述數據計算</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <small class="d-block text-muted mt-2">外部來源可能要求 Cookie、驗證碼或以表單送出股票代碼；連結開啟的是程式實際使用的資料服務或其官方查詢頁。</small>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.calculation-audit { border-top: 2px solid #dee2e6; padding-top: 1rem; }
.audit-table { min-width: 960px; font-size: .86rem; }
.audit-table th:nth-child(1) { width: 14%; }
.audit-table th:nth-child(2) { width: 25%; }
.audit-table th:nth-child(3) { width: 38%; }
.audit-table th:nth-child(4) { width: 23%; }
code { color: #842029; white-space: normal; }
</style>
