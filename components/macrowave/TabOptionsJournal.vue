<template>
  <div class="journal-dashboard">
    <div class="header flex-column align-items-start gap-3">
      <div class="d-flex justify-content-between w-100 align-items-center flex-wrap gap-3">
        <h2 class="title m-0">📖 選擇權貸方交易日誌 (Credit Spreads Journal)</h2>
        <div class="export-actions">
          <button class="export-btn csv" @click="exportCSV">📥 匯出 CSV</button>
          <button class="export-btn json" @click="exportJSON">📥 匯出 JSON</button>
          <button class="export-btn import" @click="triggerImport">📤 匯入 JSON</button>
          <input type="file" ref="fileInput" accept=".json" style="display: none" @change="handleImport" />
        </div>
      </div>
      
      <div class="view-toggles">
        <button class="view-btn" :class="{ active: viewMode === 'calendar' }" @click="viewMode = 'calendar'">
          📅 交易日曆與編輯
        </button>
        <button class="view-btn" :class="{ active: viewMode === 'summary' }" @click="viewMode = 'summary'">
          🎯 到期結算總覽
        </button>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 模式一：交易日曆與編輯 -->
    <!-- ========================================== -->
    <div class="journal-layout mt-3" v-if="viewMode === 'calendar'">
      <div class="calendar-section">
        <div class="calendar-header">
          <button @click="changeMonth(-1)" class="btn-icon">◀</button>
          <h3 class="current-month">{{ currentYear }} 年 {{ currentMonth + 1 }} 月</h3>
          <button @click="changeMonth(1)" class="btn-icon">▶</button>
        </div>
        
        <div class="calendar-grid">
          <div class="weekday">日</div><div class="weekday">一</div><div class="weekday">二</div>
          <div class="weekday">三</div><div class="weekday">四</div><div class="weekday">五</div><div class="weekday">六</div>
          
          <div v-for="blank in firstDayOffset" :key="'blank-' + blank" class="calendar-day empty"></div>
          
          <div 
            v-for="day in daysInMonth" 
            :key="'day-' + day" 
            class="calendar-day"
            :class="{ 
              'active': isSelectedDate(day), 
              'has-trade': hasTradeOnDate(day),
              'today': isToday(day)
            }"
            @click="selectDate(day)"
          >
            <span class="day-number">{{ day }}</span>
            <div class="trade-dots" v-if="hasTradeOnDate(day)">
              <span class="dot"></span>
            </div>
          </div>
        </div>

        <div class="daily-trades-list mt-4">
          <h4 class="text-white mb-3">📅 {{ selectedDateStr }} 交易紀錄</h4>
          <div v-if="dailyTrades.length === 0" class="text-muted text-center p-3">
            本日無交易紀錄
          </div>
          <div 
            v-for="trade in dailyTrades" 
            :key="trade.id" 
            class="trade-card"
            :class="trade.status === 'closed' ? (trade.pnl > 0 ? 'win' : (trade.pnl === 0 ? 'zero' : 'loss')) : 'open'"
          >
            <div class="trade-card-header">
              <span class="fw-bold text-white fs-5">{{ trade.ticker }}</span>
              <span class="strategy-badge">{{ getStrategyName(trade.strategy) }}</span>
            </div>
            <div class="trade-card-body">
              <div class="trade-detail d-flex flex-wrap gap-3 mb-2">
                <span class="color-credit">🟢 建倉: {{ trade.date }}</span>
                <span class="color-debit" v-if="trade.exit_date">🔴 平倉: {{ trade.exit_date }}</span>
                <span class="text-info">⏳ 到期: {{ trade.expiry }}</span>
              </div>
              
              <div class="trade-detail strikes-detail">
                履約價: 
                <span v-if="trade.strategy === 'bullPut'" class="fw-bold text-white">
                  Put (賣: {{ trade.strikes.shortPut }}, 買: {{ trade.strikes.longPut }})
                </span>
                <span v-if="trade.strategy === 'bearCall'" class="fw-bold text-white">
                  Call (賣: {{ trade.strikes.shortCall }}, 買: {{ trade.strikes.longCall }})
                </span>
                <span v-if="trade.strategy === 'ironCondor'" class="fw-bold text-white">
                  P(買:{{ trade.strikes.longPut }}, 賣:{{ trade.strikes.shortPut }}) / 
                  C(賣:{{ trade.strikes.shortCall }}, 買:{{ trade.strikes.longCall }})
                </span>
                <span v-if="trade.strategy === 'vertical'" class="fw-bold text-muted">
                  舊版紀錄 (S:{{ trade.strikes.short }}, L:{{ trade.strikes.long }})
                </span>
              </div>

              <div class="trade-detail">口數: {{ trade.contracts }}</div>
              <div class="trade-detail color-credit" v-if="trade.entry_price !== null">
                建倉時每口平均收租 (Credit): +${{ Number(trade.entry_price).toFixed(2) }}
              </div>
              
              <div class="risk-box mt-2 mb-2" v-if="trade.entry_price !== null">
                <div class="d-flex justify-content-between mb-1 color-profit fs-7">
                  <span>✅ 最大收益 (總計 / 每口):</span>
                  <span class="fw-bold">
                    +${{ getTradeStats(trade).maxProfit.toFixed(2) }} 
                    <span class="text-muted opacity-75">(+${{ getTradeStats(trade).perContractProfit.toFixed(2) }})</span>
                  </span>
                </div>
                <div class="d-flex justify-content-between color-loss fs-7">
                  <span>❌ 最大虧損 (總計 / 每口):</span>
                  <span class="fw-bold">
                    -${{ getTradeStats(trade).maxLoss.toFixed(2) }} 
                    <span class="text-muted opacity-75">(-${{ getTradeStats(trade).perContractLoss.toFixed(2) }})</span>
                  </span>
                </div>
              </div>

              <div class="trade-detail color-debit mt-2" v-if="getExitSummary(trade).hasExit">
                提前平倉付回總金額: -${{ (getExitSummary(trade).totalDebitDollars / 100).toFixed(2) }}
                <span class="text-muted fs-7 ml-2">(平均每口 -${{ getExitSummary(trade).avgDebit.toFixed(2) }})</span>
              </div>
              
              <div class="trade-pnl mt-3 pt-2 border-top border-secondary fw-bold fs-6" v-if="trade.status === 'closed' || trade.pnl !== 0">
                {{ trade.status === 'closed' ? '提前平倉最後總損益 (x100股)' : '未平倉暫時損益' }}: 
                <span :class="getPnlColorClass(trade.pnl)">
                  {{ trade.pnl === 0 ? '$0.00' : (trade.pnl > 0 ? '+' : '-') + '$' + Math.abs(trade.pnl).toFixed(2) }}
                </span>
              </div>
            </div>
            <div class="trade-card-actions mt-3">
              <button class="action-btn view-btn" @click="openPayoffChart(trade)">📊 預覽到期圖</button>
              <button class="action-btn edit-btn" @click="editTrade(trade)">編輯 / 登錄平倉</button>
              <button class="action-btn delete-btn" @click="deleteTrade(trade.id)">刪除</button>
            </div>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="text-white mb-4 border-bottom border-secondary pb-2">
          {{ isEditing ? '✏️ 編輯交易' : '📝 新增交易' }} 
        </h3>
        
        <form @submit.prevent="saveTrade" class="trade-form">
          <div class="d-flex flex-wrap gap-3 mb-3">
            <div class="form-group flex-fill mb-0">
              <label>股票代號 (Ticker)</label>
              <input type="text" v-model="form.ticker" required placeholder="例: SPY" class="dark-input" />
            </div>
            <div class="form-group flex-fill mb-0">
              <label>建倉日期 (Open Date)</label>
              <input type="date" v-model="form.date" required class="dark-input" />
            </div>
          </div>

          <div class="form-group">
            <label>策略類型</label>
            <select v-model="form.strategy" class="dark-input" @change="resetStrikes">
              <option value="bullPut">📉 賣權多頭 (Bull Put Spread)</option>
              <option value="bearCall">📈 買權空頭 (Bear Call Spread)</option>
              <option value="ironCondor">🦅 鐵鷹 (Iron Condor)</option>
            </select>
          </div>

          <div class="form-group">
            <label>到期日 (Expiration)</label>
            <input type="date" v-model="form.expiry" required class="dark-input" />
          </div>

          <div v-if="form.strategy === 'bullPut'" class="strikes-grid">
            <div class="form-group"><label class="text-danger">賣出 (Short) Put</label><input type="number" step="0.5" v-model.number="form.strikes.shortPut" required class="dark-input" /></div>
            <div class="form-group"><label class="text-success">買入 (Long) Put</label><input type="number" step="0.5" v-model.number="form.strikes.longPut" required class="dark-input" /></div>
          </div>

          <div v-if="form.strategy === 'bearCall'" class="strikes-grid">
            <div class="form-group"><label class="text-danger">賣出 (Short) Call</label><input type="number" step="0.5" v-model.number="form.strikes.shortCall" required class="dark-input" /></div>
            <div class="form-group"><label class="text-success">買入 (Long) Call</label><input type="number" step="0.5" v-model.number="form.strikes.longCall" required class="dark-input" /></div>
          </div>

          <div v-if="form.strategy === 'ironCondor'" class="strikes-grid-4">
            <div class="form-group"><label class="text-success">買入 Put</label><input type="number" step="0.5" v-model.number="form.strikes.longPut" required class="dark-input" /></div>
            <div class="form-group"><label class="text-danger">賣出 Put</label><input type="number" step="0.5" v-model.number="form.strikes.shortPut" required class="dark-input" /></div>
            <div class="form-group"><label class="text-danger">賣出 Call</label><input type="number" step="0.5" v-model.number="form.strikes.shortCall" required class="dark-input" /></div>
            <div class="form-group"><label class="text-success">買入 Call</label><input type="number" step="0.5" v-model.number="form.strikes.longCall" required class="dark-input" /></div>
          </div>

          <div class="d-flex flex-wrap gap-3">
            <div class="form-group flex-fill">
              <label>口數 (Contracts)</label>
              <input type="number" min="1" v-model.number="form.contracts" required class="dark-input" />
            </div>
            <div class="form-group flex-fill">
              <label class="color-credit">建倉時每口平均收租 (Credit)</label>
              <input type="number" step="0.01" v-model.number="form.entryPrice" required class="dark-input" />
            </div>
          </div>

          <div class="border-top border-secondary pt-3 mt-2">
            <h5 class="text-warning mb-3">🚪 平倉紀錄區 (未平倉請留空)</h5>
            
            <div class="form-group">
              <label class="text-warning">平倉日期 (Close Date)</label>
              <input type="date" v-model="form.exitDate" class="dark-input" />
            </div>

            <div v-if="form.strategy !== 'ironCondor'">
              <label class="color-debit mb-2 d-block">提前平倉每口付回 (Debit) 與 口數</label>
              <div v-for="(fill, idx) in form.strikes.exitFillsSingle" :key="'sing-'+idx" class="d-flex gap-2 mb-2 align-items-center">
                <input type="number" step="0.01" v-model.number="fill.price" class="dark-input flex-fill" placeholder="價位 (歸零填 0)" />
                <span class="text-muted">x</span>
                <input type="number" min="1" v-model.number="fill.contracts" class="dark-input" style="width: 80px" placeholder="口數" />
                <button type="button" class="btn-icon text-danger" v-if="form.strikes.exitFillsSingle.length > 1" @click="form.strikes.exitFillsSingle.splice(idx, 1)">✖</button>
              </div>
              <button type="button" class="btn-add-fill" @click="form.strikes.exitFillsSingle.push({price: null, contracts: 1})">➕ 新增平倉批次</button>
            </div>

            <div class="strikes-grid" v-if="form.strategy === 'ironCondor'">
              <div>
                <label class="color-debit mb-2 d-block">Put 邊平倉付回與口數</label>
                <div v-for="(fill, idx) in form.strikes.exitFillsPut" :key="'put-'+idx" class="d-flex gap-2 mb-2 align-items-center">
                  <input type="number" step="0.01" v-model.number="fill.price" class="dark-input flex-fill" placeholder="價位" />
                  <span class="text-muted">x</span>
                  <input type="number" min="1" v-model.number="fill.contracts" class="dark-input" style="width: 80px" placeholder="口數" />
                  <button type="button" class="btn-icon text-danger" v-if="form.strikes.exitFillsPut.length > 1" @click="form.strikes.exitFillsPut.splice(idx, 1)">✖</button>
                </div>
                <button type="button" class="btn-add-fill" @click="form.strikes.exitFillsPut.push({price: null, contracts: 1})">➕ 新增批次</button>
              </div>
              
              <div>
                <label class="color-debit mb-2 d-block">Call 邊平倉付回與口數</label>
                <div v-for="(fill, idx) in form.strikes.exitFillsCall" :key="'call-'+idx" class="d-flex gap-2 mb-2 align-items-center">
                  <input type="number" step="0.01" v-model.number="fill.price" class="dark-input flex-fill" placeholder="價位" />
                  <span class="text-muted">x</span>
                  <input type="number" min="1" v-model.number="fill.contracts" class="dark-input" style="width: 80px" placeholder="口數" />
                  <button type="button" class="btn-icon text-danger" v-if="form.strikes.exitFillsCall.length > 1" @click="form.strikes.exitFillsCall.splice(idx, 1)">✖</button>
                </div>
                <button type="button" class="btn-add-fill" @click="form.strikes.exitFillsCall.push({price: null, contracts: 1})">➕ 新增批次</button>
              </div>
            </div>
          </div>

          <div class="calc-preview mt-4" v-if="formStats">
            <h5 class="calc-title mb-3">💡 交易試算預覽</h5>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">到期最大收益 (總計 / 每口):</span>
              <span class="color-profit fw-bold">+${{ formStats.maxProfit.toFixed(2) }} <span class="fs-7 text-muted">(+${{ formStats.perContractProfit.toFixed(2) }})</span></span>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">到期最大虧損 (總計 / 每口):</span>
              <span class="color-loss fw-bold">-${{ formStats.maxLoss.toFixed(2) }} <span class="fs-7 text-muted">(-${{ formStats.perContractLoss.toFixed(2) }})</span></span>
            </div>
            
            <div v-if="formStats.exitDetails" class="pt-2 mt-2 border-top border-secondary">
              <div class="text-white mb-2 fw-bold">👉 平倉實際損益拆解：</div>
              <div class="d-flex justify-content-between fs-7 mb-1 color-credit">
                <span>➕ 建倉總收租:</span><span>+${{ formStats.maxProfit.toFixed(2) }}</span>
              </div>
              
              <template v-if="form.strategy === 'ironCondor'">
                <div class="d-flex justify-content-between fs-7 mb-1 color-debit" v-if="formStats.exitDetails.putDebit > 0">
                  <span>➖ Put 邊總付回:</span><span>-${{ formStats.exitDetails.putDebit.toFixed(2) }}</span>
                </div>
                <div class="d-flex justify-content-between fs-7 mb-1 color-debit" v-if="formStats.exitDetails.callDebit > 0">
                  <span>➖ Call 邊總付回:</span><span>-${{ formStats.exitDetails.callDebit.toFixed(2) }}</span>
                </div>
              </template>
              <template v-else>
                <div class="d-flex justify-content-between fs-7 mb-1 color-debit">
                  <span>➖ 提前平倉付回總付出金額:</span><span>-${{ formStats.exitDetails.totalDebitDollars.toFixed(2) }}</span>
                </div>
              </template>

              <div class="d-flex justify-content-between fs-7 mt-2 pt-2 border-top border-secondary">
                 <span class="text-muted">平均每口平倉付回 (Avg Debit):</span>
                 <span class="color-debit">-${{ formStats.exitDetails.avgDebit.toFixed(2) }}</span>
              </div>

              <div class="d-flex justify-content-between mt-2 pt-2 border-top border-secondary">
                <span class="text-white fw-bold">提前平倉最後總損益 (x100股):</span>
                <span class="fw-bold fs-5" :class="formStats.exitDetails.pnl === 0 ? 'color-zero' : (formStats.exitDetails.pnl > 0 ? 'color-profit' : 'color-loss')">
                  {{ formStats.exitDetails.pnl === 0 ? '$0.00' : (formStats.exitDetails.pnl > 0 ? '+' : '-') + '$' + Math.abs(formStats.exitDetails.pnl).toFixed(2) }}
                </span>
              </div>
            </div>
          </div>

          <div class="form-actions mt-4">
            <button type="submit" class="submit-btn w-100">{{ isEditing ? '儲存紀錄' : '新增紀錄' }}</button>
            <button type="button" @click="cancelEdit" class="cancel-btn w-100 mt-2" v-if="isEditing">取消</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- 模式二：到期結算總覽介面 -->
    <!-- ========================================== -->
    <div v-else-if="viewMode === 'summary'" class="summary-layout mt-3">
      <div v-if="expirySummary.length === 0" class="text-muted text-center p-5 fs-5">
        目前沒有任何交易紀錄
      </div>

      <div v-for="group in expirySummary" :key="group.expiry" class="expiry-group-card mb-4">
        <div class="expiry-header d-flex justify-content-between align-items-start flex-wrap gap-3">
          <h3 class="m-0 text-white mb-3">⌛ <span class="text-warning">到期日:</span> {{ group.expiry }}</h3>
          <div class="summary-stats d-flex flex-wrap gap-2">
            <div class="stat-item color-credit flex-fill">
              <div class="fs-7 opacity-75">✅ 該群組建倉總收租</div>
              <div>+${{ group.totalCredit.toFixed(2) }}</div>
            </div>
            <div class="stat-item text-info flex-fill">
              <div class="fs-7 opacity-75">⏳ 未平倉剩餘價值 (放至歸零)</div>
              <div>+${{ group.openCredit.toFixed(2) }}</div>
            </div>
            <div class="stat-item flex-fill" :class="getPnlColorClass(group.realizedPnL)">
              <div class="fs-7 opacity-75">🚪 已平倉實際損益 (含單邊)</div>
              <div>{{ group.realizedPnL === 0 ? '$0.00' : (group.realizedPnL > 0 ? '+' : '-') + '$' + Math.abs(group.realizedPnL).toFixed(2) }}</div>
            </div>
          </div>
        </div>

        <div class="table-responsive mt-3">
          <table class="summary-table w-100">
            <thead>
              <tr>
                <th>狀態</th>
                <th>代號</th>
                <th>策略</th>
                <th>履約價細節</th>
                <th>口數</th>
                <th>建倉時每口平均收租<br/><span class="fs-7 color-credit">(Credit)</span></th>
                <th>該筆總收租金額<br/><span class="fs-7 color-credit">(x100股)</span></th>
                <th>提前平倉每口平均付回<br/><span class="fs-7 color-debit">(Debit)</span></th>
                <th>收租和付回差價</th>
                <th>提前平倉付回總付出金額<br/><span class="fs-7 color-debit">(x100股)</span></th>
                <th>提前平倉每口最後平均損益<br/><span class="fs-7 text-muted">(x100股)</span></th>
                <th>提前平倉最後總損益<br/><span class="fs-7 text-muted">(x100股)</span></th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trade in group.trades" :key="trade.id" :class="trade.status === 'closed' ? 'dimmed-row' : ''">
                <td>
                  <span class="badge" :class="trade.status === 'closed' ? 'bg-secondary' : 'bg-primary'">
                    {{ trade.status === 'closed' ? '已平倉' : '持倉中' }}
                  </span>
                </td>
                <td class="fw-bold text-white fs-6">{{ trade.ticker }}</td>
                <td class="text-muted">{{ getStrategyName(trade.strategy) }}</td>
                <td class="fs-7">
                  <span v-if="trade.strategy === 'bullPut'">P(賣:{{trade.strikes.shortPut}}, 買:{{trade.strikes.longPut}})</span>
                  <span v-else-if="trade.strategy === 'bearCall'">C(賣:{{trade.strikes.shortCall}}, 買:{{trade.strikes.longCall}})</span>
                  <span v-else-if="trade.strategy === 'ironCondor'">P(買:{{trade.strikes.longPut}}, 賣:{{trade.strikes.shortPut}}) / C(賣:{{trade.strikes.shortCall}}, 買:{{trade.strikes.longCall}})</span>
                  <span v-else>S:{{trade.strikes.short}}, L:{{trade.strikes.long}}</span>
                </td>
                <td>{{ trade.contracts }}</td>
                
                <td :class="getNumberColorClass(trade.entry_price, 'credit')">
                  {{ trade.entry_price === 0 ? '$0.00' : '+$' + Number(trade.entry_price).toFixed(2) }}
                </td>
                <td :class="getNumberColorClass(trade.entry_price * 100 * trade.contracts, 'credit')" class="fw-bold">
                  {{ (trade.entry_price * 100 * trade.contracts) === 0 ? '$0.00' : '+$' + (trade.entry_price * 100 * trade.contracts).toFixed(2) }}
                </td>
                
                <td>
                  <span v-if="getExitSummary(trade).hasExit" :class="getNumberColorClass(getExitSummary(trade).avgDebit, 'debit')">
                    {{ getExitSummary(trade).avgDebit === 0 ? '$0.00' : '-$' + getExitSummary(trade).avgDebit.toFixed(2) }}
                    <span v-if="getExitSummary(trade).isMultiple" class="text-muted fs-7">(平均)</span>
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <span v-if="getExitSummary(trade).hasExit" class="fw-bold" :class="getPnlColorClass(getPriceDiff(trade))">
                    {{ getPriceDiff(trade) === 0 ? '$0.00' : (getPriceDiff(trade) > 0 ? '+' : '-') + '$' + Math.abs(getPriceDiff(trade)).toFixed(2) }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <span v-if="getExitSummary(trade).hasExit" class="fw-bold" :class="getNumberColorClass(getExitSummary(trade).totalDebitDollars, 'debit')">
                    {{ getExitSummary(trade).totalDebitDollars === 0 ? '$0.00' : '-$' + getExitSummary(trade).totalDebitDollars.toFixed(2) }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <span v-if="getExitSummary(trade).hasExit" class="fw-bold" :class="getPnlColorClass(getExitPnlPerContract(trade))">
                    {{ getExitPnlPerContract(trade) === 0 ? '$0.00' : (getExitPnlPerContract(trade) > 0 ? '+' : '-') + '$' + Math.abs(getExitPnlPerContract(trade)).toFixed(2) }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <span v-if="getExitSummary(trade).hasExit" class="fw-bold fs-6" :class="getPnlColorClass(trade.pnl)">
                    {{ trade.pnl === 0 ? '$0.00' : (trade.pnl > 0 ? '+' : '-') + '$' + Math.abs(trade.pnl).toFixed(2) }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                
                <td>
                  <div class="d-flex gap-2">
                    <button class="action-icon-btn" @click="openPayoffChart(trade)" title="預覽到期圖">📊</button>
                    <button class="action-icon-btn" @click="editTrade(trade)" title="編輯/登錄平倉">✏️</button>
                    <button class="action-icon-btn" @click="deleteTrade(trade.id)" title="刪除">🗑️</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal 編輯表單 (模式二專用) -->
    <div v-if="isEditing && viewMode === 'summary'" class="chart-modal-overlay" @click.self="cancelEdit">
      <div class="form-modal-content">
        <div class="chart-modal-header border-bottom border-secondary pb-3 mb-3 d-flex justify-content-between align-items-center">
          <h4 class="m-0 fw-bold text-white">✏️ 編輯交易 / 登錄平倉</h4>
          <button class="close-btn" @click="cancelEdit">✖</button>
        </div>
        
        <!-- 表單 HTML 直接展開於此 -->
        <form @submit.prevent="saveTrade" class="trade-form">
          <div class="d-flex flex-wrap gap-3 mb-3">
            <div class="form-group flex-fill mb-0">
              <label>股票代號 (Ticker)</label>
              <input type="text" v-model="form.ticker" required placeholder="例: SPY" class="dark-input" />
            </div>
            <div class="form-group flex-fill mb-0">
              <label>建倉日期 (Open Date)</label>
              <input type="date" v-model="form.date" required class="dark-input" />
            </div>
          </div>

          <div class="form-group">
            <label>策略類型</label>
            <select v-model="form.strategy" class="dark-input" @change="resetStrikes">
              <option value="bullPut">📉 賣權多頭 (Bull Put Spread)</option>
              <option value="bearCall">📈 買權空頭 (Bear Call Spread)</option>
              <option value="ironCondor">🦅 鐵鷹 (Iron Condor)</option>
            </select>
          </div>

          <div class="form-group">
            <label>到期日 (Expiration)</label>
            <input type="date" v-model="form.expiry" required class="dark-input" />
          </div>

          <div v-if="form.strategy === 'bullPut'" class="strikes-grid">
            <div class="form-group"><label class="text-danger">賣出 (Short) Put</label><input type="number" step="0.5" v-model.number="form.strikes.shortPut" required class="dark-input" /></div>
            <div class="form-group"><label class="text-success">買入 (Long) Put</label><input type="number" step="0.5" v-model.number="form.strikes.longPut" required class="dark-input" /></div>
          </div>

          <div v-if="form.strategy === 'bearCall'" class="strikes-grid">
            <div class="form-group"><label class="text-danger">賣出 (Short) Call</label><input type="number" step="0.5" v-model.number="form.strikes.shortCall" required class="dark-input" /></div>
            <div class="form-group"><label class="text-success">買入 (Long) Call</label><input type="number" step="0.5" v-model.number="form.strikes.longCall" required class="dark-input" /></div>
          </div>

          <div v-if="form.strategy === 'ironCondor'" class="strikes-grid-4">
            <div class="form-group"><label class="text-success">買入 Put</label><input type="number" step="0.5" v-model.number="form.strikes.longPut" required class="dark-input" /></div>
            <div class="form-group"><label class="text-danger">賣出 Put</label><input type="number" step="0.5" v-model.number="form.strikes.shortPut" required class="dark-input" /></div>
            <div class="form-group"><label class="text-danger">賣出 Call</label><input type="number" step="0.5" v-model.number="form.strikes.shortCall" required class="dark-input" /></div>
            <div class="form-group"><label class="text-success">買入 Call</label><input type="number" step="0.5" v-model.number="form.strikes.longCall" required class="dark-input" /></div>
          </div>

          <div class="d-flex flex-wrap gap-3">
            <div class="form-group flex-fill">
              <label>口數 (Contracts)</label>
              <input type="number" min="1" v-model.number="form.contracts" required class="dark-input" />
            </div>
            <div class="form-group flex-fill">
              <label class="color-credit">建倉時每口平均收租 (Credit)</label>
              <input type="number" step="0.01" v-model.number="form.entryPrice" required class="dark-input" />
            </div>
          </div>

          <div class="border-top border-secondary pt-3 mt-2">
            <h5 class="text-warning mb-3">🚪 平倉紀錄區 (未平倉請留空)</h5>
            
            <div class="form-group">
              <label class="text-warning">平倉日期 (Close Date)</label>
              <input type="date" v-model="form.exitDate" class="dark-input" />
            </div>

            <div v-if="form.strategy !== 'ironCondor'">
              <label class="color-debit mb-2 d-block">提前平倉每口付回 (Debit) 與 口數</label>
              <div v-for="(fill, idx) in form.strikes.exitFillsSingle" :key="'m-sing-'+idx" class="d-flex gap-2 mb-2 align-items-center">
                <input type="number" step="0.01" v-model.number="fill.price" class="dark-input flex-fill" placeholder="價位 (歸零填 0)" />
                <span class="text-muted">x</span>
                <input type="number" min="1" v-model.number="fill.contracts" class="dark-input" style="width: 80px" placeholder="口數" />
                <button type="button" class="btn-icon text-danger" v-if="form.strikes.exitFillsSingle.length > 1" @click="form.strikes.exitFillsSingle.splice(idx, 1)">✖</button>
              </div>
              <button type="button" class="btn-add-fill" @click="form.strikes.exitFillsSingle.push({price: null, contracts: 1})">➕ 新增平倉批次</button>
            </div>

            <div class="strikes-grid" v-if="form.strategy === 'ironCondor'">
              <div>
                <label class="color-debit mb-2 d-block">Put 邊平倉付回與口數</label>
                <div v-for="(fill, idx) in form.strikes.exitFillsPut" :key="'m-put-'+idx" class="d-flex gap-2 mb-2 align-items-center">
                  <input type="number" step="0.01" v-model.number="fill.price" class="dark-input flex-fill" placeholder="價位" />
                  <span class="text-muted">x</span>
                  <input type="number" min="1" v-model.number="fill.contracts" class="dark-input" style="width: 80px" placeholder="口數" />
                  <button type="button" class="btn-icon text-danger" v-if="form.strikes.exitFillsPut.length > 1" @click="form.strikes.exitFillsPut.splice(idx, 1)">✖</button>
                </div>
                <button type="button" class="btn-add-fill" @click="form.strikes.exitFillsPut.push({price: null, contracts: 1})">➕ 新增批次</button>
              </div>
              
              <div>
                <label class="color-debit mb-2 d-block">Call 邊平倉付回與口數</label>
                <div v-for="(fill, idx) in form.strikes.exitFillsCall" :key="'m-call-'+idx" class="d-flex gap-2 mb-2 align-items-center">
                  <input type="number" step="0.01" v-model.number="fill.price" class="dark-input flex-fill" placeholder="價位" />
                  <span class="text-muted">x</span>
                  <input type="number" min="1" v-model.number="fill.contracts" class="dark-input" style="width: 80px" placeholder="口數" />
                  <button type="button" class="btn-icon text-danger" v-if="form.strikes.exitFillsCall.length > 1" @click="form.strikes.exitFillsCall.splice(idx, 1)">✖</button>
                </div>
                <button type="button" class="btn-add-fill" @click="form.strikes.exitFillsCall.push({price: null, contracts: 1})">➕ 新增批次</button>
              </div>
            </div>
          </div>

          <div class="calc-preview mt-4" v-if="formStats">
            <h5 class="calc-title mb-3">💡 交易試算預覽</h5>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">到期最大收益 (總計 / 每口):</span>
              <span class="color-profit fw-bold">+${{ formStats.maxProfit.toFixed(2) }} <span class="fs-7 text-muted">(+${{ formStats.perContractProfit.toFixed(2) }})</span></span>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">到期最大虧損 (總計 / 每口):</span>
              <span class="color-loss fw-bold">-${{ formStats.maxLoss.toFixed(2) }} <span class="fs-7 text-muted">(-${{ formStats.perContractLoss.toFixed(2) }})</span></span>
            </div>
            
            <div v-if="formStats.exitDetails" class="pt-2 mt-2 border-top border-secondary">
              <div class="text-white mb-2 fw-bold">👉 平倉實際損益拆解：</div>
              <div class="d-flex justify-content-between fs-7 mb-1 color-credit">
                <span>➕ 建倉總收租:</span><span>+${{ formStats.maxProfit.toFixed(2) }}</span>
              </div>
              
              <template v-if="form.strategy === 'ironCondor'">
                <div class="d-flex justify-content-between fs-7 mb-1 color-debit" v-if="formStats.exitDetails.putDebit > 0">
                  <span>➖ Put 邊總付回:</span><span>-${{ formStats.exitDetails.putDebit.toFixed(2) }}</span>
                </div>
                <div class="d-flex justify-content-between fs-7 mb-1 color-debit" v-if="formStats.exitDetails.callDebit > 0">
                  <span>➖ Call 邊總付回:</span><span>-${{ formStats.exitDetails.callDebit.toFixed(2) }}</span>
                </div>
              </template>
              <template v-else>
                <div class="d-flex justify-content-between fs-7 mb-1 color-debit">
                  <span>➖ 提前平倉付回總付出金額:</span><span>-${{ formStats.exitDetails.totalDebitDollars.toFixed(2) }}</span>
                </div>
              </template>

              <div class="d-flex justify-content-between fs-7 mt-2 pt-2 border-top border-secondary">
                 <span class="text-muted">平均每口平倉付回 (Avg Debit):</span>
                 <span class="color-debit">-${{ formStats.exitDetails.avgDebit.toFixed(2) }}</span>
              </div>

              <div class="d-flex justify-content-between mt-2 pt-2 border-top border-secondary">
                <span class="text-white fw-bold">提前平倉最後總損益 (x100股):</span>
                <span class="fw-bold fs-5" :class="formStats.exitDetails.pnl === 0 ? 'color-zero' : (formStats.exitDetails.pnl > 0 ? 'color-profit' : 'color-loss')">
                  {{ formStats.exitDetails.pnl === 0 ? '$0.00' : (formStats.exitDetails.pnl > 0 ? '+' : '-') + '$' + Math.abs(formStats.exitDetails.pnl).toFixed(2) }}
                </span>
              </div>
            </div>
          </div>

          <div class="form-actions mt-4">
            <button type="submit" class="submit-btn w-100">儲存紀錄</button>
            <button type="button" @click="cancelEdit" class="cancel-btn w-100 mt-2">取消</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 到期損益圖 Modal -->
    <div v-if="isChartModalOpen" class="chart-modal-overlay" @click.self="closePayoffChart">
      <div class="chart-modal-content">
        <div class="chart-modal-header border-bottom border-secondary pb-3 mb-3 d-flex justify-content-between align-items-center">
          <h4 class="m-0 fw-bold text-white fs-5">📊 {{ chartTradeData?.ticker }} 到期損益預測圖</h4>
          <button class="close-btn" @click="closePayoffChart">✖</button>
        </div>
        <div class="chart-modal-body">
          <div id="payoff-chart" style="width: 100%; height: 400px;"></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import * as echarts from 'echarts';

const supabase = useSupabaseClient();
const viewMode = ref('calendar');

const date = new Date();
const currentYear = ref(date.getFullYear());
const currentMonth = ref(date.getMonth());
const selectedDay = ref(date.getDate());

const selectedDateStr = computed(() => {
  return `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-${String(selectedDay.value).padStart(2, '0')}`;
});

const daysInMonth = computed(() => new Date(currentYear.value, currentMonth.value + 1, 0).getDate());
const firstDayOffset = computed(() => new Date(currentYear.value, currentMonth.value, 1).getDay());

const changeMonth = (delta) => {
  let newMonth = currentMonth.value + delta;
  if (newMonth > 11) { newMonth = 0; currentYear.value++; }
  else if (newMonth < 0) { newMonth = 11; currentYear.value--; }
  currentMonth.value = newMonth;
  selectedDay.value = 1; 
};

const selectDate = (day) => { selectedDay.value = day; };
const isSelectedDate = (day) => day === selectedDay.value;
const isToday = (day) => {
  const today = new Date();
  return day === today.getDate() && currentMonth.value === today.getMonth() && currentYear.value === today.getFullYear();
};

const getNumberColorClass = (val, type) => {
  if (val === 0 || Math.abs(val) < 0.0001) return 'color-zero';
  if (type === 'credit') return 'color-credit';
  if (type === 'debit') return 'color-debit';
  return val > 0 ? 'color-profit' : 'color-loss';
};

const getPnlColorClass = (val) => {
  if (val === 0 || Math.abs(val) < 0.0001) return 'color-zero';
  return val > 0 ? 'color-profit' : 'color-loss';
};

const allTrades = ref([]);

const fetchTrades = async () => {
  const { data, error } = await supabase.from('macrowave_options_journal').select('*').order('created_at', { ascending: false });
  if (!error) allTrades.value = data || [];
};

onMounted(() => { fetchTrades(); });

const dailyTrades = computed(() => { return allTrades.value.filter(t => t.date === selectedDateStr.value); });
const hasTradeOnDate = (day) => {
  const checkDate = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  return allTrades.value.some(t => t.date === checkDate);
};

const getExitSummary = (trade) => {
  if (trade.strategy === 'ironCondor') {
    let putDebit = 0, callDebit = 0, hasExit = false, isMultiple = false;
    
    if (trade.strikes.exitFillsPut && trade.strikes.exitFillsPut.length) {
        if(trade.strikes.exitFillsPut.length > 1) isMultiple = true;
        trade.strikes.exitFillsPut.forEach(f => { if(f.price !== null && f.price !== '') { putDebit += Number(f.price) * Number(f.contracts); hasExit = true; }});
    } else if (trade.strikes.exitPut !== null && trade.strikes.exitPut !== undefined) {
        putDebit = Number(trade.strikes.exitPut) * trade.contracts;
        hasExit = true;
    }

    if (trade.strikes.exitFillsCall && trade.strikes.exitFillsCall.length) {
        if(trade.strikes.exitFillsCall.length > 1) isMultiple = true;
        trade.strikes.exitFillsCall.forEach(f => { if(f.price !== null && f.price !== '') { callDebit += Number(f.price) * Number(f.contracts); hasExit = true; }});
    } else if (trade.strikes.exitCall !== null && trade.strikes.exitCall !== undefined) {
        callDebit = Number(trade.strikes.exitCall) * trade.contracts;
        hasExit = true;
    }
    
    const totalDebitDollars = (putDebit + callDebit) * 100;
    const avgDebit = trade.contracts > 0 ? (putDebit + callDebit) / trade.contracts : 0;
    return { hasExit, totalDebitDollars, avgDebit, putDebit: putDebit * 100, callDebit: callDebit * 100, isMultiple };
  } else {
    let debit = 0, hasExit = false, isMultiple = false;
    if (trade.strikes.exitFillsSingle && trade.strikes.exitFillsSingle.length) {
        if(trade.strikes.exitFillsSingle.length > 1) isMultiple = true;
        trade.strikes.exitFillsSingle.forEach(f => { if(f.price !== null && f.price !== '') { debit += Number(f.price) * Number(f.contracts); hasExit = true; }});
    } else if (trade.exit_price !== null && trade.exit_price !== undefined) {
        debit = Number(trade.exit_price) * trade.contracts;
        hasExit = true;
    }
    const totalDebitDollars = debit * 100;
    const avgDebit = trade.contracts > 0 ? debit / trade.contracts : 0;
    return { hasExit, totalDebitDollars, avgDebit, isMultiple };
  }
};

const getPriceDiff = (trade) => {
  const entry = Number(trade.entry_price) || 0;
  const exitAvg = getExitSummary(trade).avgDebit || 0;
  return entry - exitAvg;
};

const getExitPnlPerContract = (trade) => {
  return getPriceDiff(trade) * 100;
};

const expirySummary = computed(() => {
  const groups = {};
  allTrades.value.forEach(trade => {
    const exp = trade.expiry;
    if (!groups[exp]) {
      groups[exp] = { expiry: exp, trades: [], totalCredit: 0, realizedPnL: 0, openCredit: 0 };
    }
    groups[exp].trades.push(trade);
    const credit = (trade.entry_price || 0) * 100 * trade.contracts;
    groups[exp].totalCredit += credit;
    if (trade.status === 'closed' || getExitSummary(trade).hasExit) {
      groups[exp].realizedPnL += (trade.pnl || 0);
    } 
    if (trade.status !== 'closed') {
      groups[exp].openCredit += credit;
    }
  });
  return Object.values(groups).sort((a, b) => new Date(a.expiry) - new Date(b.expiry));
});

const getStrategyName = (val) => {
  if (val === 'bullPut') return '賣權多頭 (Bull Put)';
  if (val === 'bearCall') return '買權空頭 (Bear Call)';
  if (val === 'ironCondor') return '鐵鷹 (Iron Condor)';
  return '垂直價差';
};

const isEditing = ref(false);
const editingId = ref(null);

const initialForm = {
  date: '', ticker: '', strategy: 'bullPut', expiry: '',
  strikes: { 
    shortPut: null, longPut: null, shortCall: null, longCall: null,
    exitFillsPut: [{ price: null, contracts: 1 }],
    exitFillsCall: [{ price: null, contracts: 1 }],
    exitFillsSingle: [{ price: null, contracts: 1 }]
  },
  contracts: 1, entryPrice: null, exitPrice: null, exitDate: ''
};
const form = ref(JSON.parse(JSON.stringify(initialForm)));

watch(selectedDateStr, (newVal) => {
  if (!isEditing.value) form.value.date = newVal;
}, { immediate: true });

const resetStrikes = () => {
  form.value.strikes = { 
    shortPut: null, longPut: null, shortCall: null, longCall: null,
    exitFillsPut: [{ price: null, contracts: 1 }],
    exitFillsCall: [{ price: null, contracts: 1 }],
    exitFillsSingle: [{ price: null, contracts: 1 }]
  };
};

const getSafeStrikes = (strategy, strikes) => {
  let sP = Number(strikes.shortPut) || 0;
  let lP = Number(strikes.longPut) || 0;
  let sC = Number(strikes.shortCall) || 0;
  let lC = Number(strikes.longCall) || 0;

  if (strategy === 'bullPut' || strategy === 'ironCondor') {
    const min = Math.min(sP, lP), max = Math.max(sP, lP);
    lP = min; sP = max;
  }
  if (strategy === 'bearCall' || strategy === 'ironCondor') {
    const min = Math.min(sC, lC), max = Math.max(sC, lC);
    sC = min; lC = max;
  }
  let s = Number(strikes.short) || 0, l = Number(strikes.long) || 0;
  return { sP, lP, sC, lC, s, l };
};

const getTradeStats = (trade) => {
  if (trade.entry_price === null) return { maxProfit: 0, maxLoss: 0, perContractProfit: 0, perContractLoss: 0 };
  const { sP, lP, sC, lC, s, l } = getSafeStrikes(trade.strategy, trade.strikes);
  let width = 0;

  if (trade.strategy === 'bullPut') width = sP - lP;
  else if (trade.strategy === 'bearCall') width = lC - sC;
  else if (trade.strategy === 'ironCondor') width = Math.max(sP - lP, lC - sC);
  else if (trade.strategy === 'vertical') width = Math.abs(s - l);

  const perContractProfit = trade.entry_price * 100;
  const perContractLoss = Math.max(0, width - trade.entry_price) * 100;
  
  return {
    maxProfit: perContractProfit * trade.contracts,
    maxLoss: perContractLoss * trade.contracts,
    perContractProfit, perContractLoss
  };
};

const formStats = computed(() => {
  const c = form.value;
  if (!c.entryPrice || !c.contracts) return null;

  const { sP, lP, sC, lC, s, l } = getSafeStrikes(c.strategy, c.strikes);
  let width = 0;

  if (c.strategy === 'bullPut') width = sP - lP;
  else if (c.strategy === 'bearCall') width = lC - sC;
  else if (c.strategy === 'ironCondor') width = Math.max(sP - lP, lC - sC);
  else if (c.strategy === 'vertical') width = Math.abs(s - l);

  const perContractProfit = c.entryPrice * 100;
  const perContractLoss = Math.max(0, width - c.entryPrice) * 100;
  const maxProfit = perContractProfit * c.contracts;
  const maxLoss = perContractLoss * c.contracts;
  
  let exitDetails = null;
  const summary = getExitSummary(form.value);

  if (summary.hasExit) {
     const pnl = maxProfit - summary.totalDebitDollars;
     exitDetails = {
         ...summary,
         pnl,
         statusText: '提前平倉最後總損益 (x100股):'
     };
  }

  if (width > 0 && width < c.entryPrice) return null; 
  return { width, maxProfit, maxLoss, perContractProfit, perContractLoss, exitDetails };
});

const saveTrade = async () => {
  const summary = getExitSummary(form.value);
  const pnl = (form.value.entryPrice * form.value.contracts * 100) - summary.totalDebitDollars;
  const isClosed = summary.hasExit; 

  const tradeData = {
    date: form.value.date, 
    ticker: form.value.ticker.toUpperCase(),
    strategy: form.value.strategy,
    expiry: form.value.expiry,
    strikes: form.value.strikes, 
    contracts: form.value.contracts,
    entry_price: form.value.entryPrice,
    exit_price: summary.hasExit ? summary.avgDebit : null, 
    exit_date: form.value.exitDate ? form.value.exitDate : null, 
    status: isClosed ? 'closed' : 'open',
    pnl: Number(pnl.toFixed(2))
  };

  if (isEditing.value) {
    await supabase.from('macrowave_options_journal').update(tradeData).eq('id', editingId.value);
  } else {
    await supabase.from('macrowave_options_journal').insert([tradeData]);
  }
  await fetchTrades();
  cancelEdit();
};

const initFills = (fills, legacyPrice, tradeContracts) => {
  if (fills && fills.length > 0) return JSON.parse(JSON.stringify(fills));
  if (legacyPrice !== null && legacyPrice !== undefined) return [{ price: legacyPrice, contracts: tradeContracts }];
  return [{ price: null, contracts: tradeContracts }];
};

const editTrade = (trade) => {
  isEditing.value = true;
  editingId.value = trade.id;
  
  form.value = {
    date: trade.date,
    ticker: trade.ticker,
    strategy: trade.strategy,
    expiry: trade.expiry,
    strikes: {
      ...trade.strikes,
      exitFillsPut: initFills(trade.strikes.exitFillsPut, trade.strikes.exitPut, trade.contracts),
      exitFillsCall: initFills(trade.strikes.exitFillsCall, trade.strikes.exitCall, trade.contracts),
      exitFillsSingle: initFills(trade.strikes.exitFillsSingle, trade.exit_price, trade.contracts)
    },
    contracts: trade.contracts,
    entryPrice: trade.entry_price,
    exitDate: trade.exit_date || ''
  };
};

const deleteTrade = async (id) => {
  if (confirm('確定要刪除這筆交易紀錄嗎？')) {
    await supabase.from('macrowave_options_journal').delete().eq('id', id);
    await fetchTrades();
    if (isEditing.value && editingId.value === id) cancelEdit();
  }
};

const cancelEdit = () => {
  isEditing.value = false;
  editingId.value = null;
  form.value = JSON.parse(JSON.stringify(initialForm));
  form.value.date = selectedDateStr.value; 
};

// ==========================================
// 匯出 / 匯入功能邏輯
// ==========================================
const fileInput = ref(null);

const exportJSON = () => {
  if (allTrades.value.length === 0) return alert('目前沒有紀錄可以匯出！');
  const dataStr = JSON.stringify(allTrades.value, null, 2);
  const blob = new Blob([dataStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `MacroWave_Options_Journal_${new Date().toISOString().split('T')[0]}.json`;
  a.click();
  URL.revokeObjectURL(url);
};

const exportCSV = () => {
  if (allTrades.value.length === 0) return alert('目前沒有紀錄可以匯出！');
  const headers = ['id', 'date', 'ticker', 'strategy', 'expiry', 'strikes', 'contracts', 'entry_price', 'exit_price', 'exit_date', 'status', 'pnl'];
  
  const rows = allTrades.value.map(t => {
    return headers.map(h => {
      let val = t[h];
      if (h === 'strikes') val = JSON.stringify(val); 
      if (val === null || val === undefined) val = '';
      val = `"${String(val).replace(/"/g, '""')}"`;
      return val;
    }).join(',');
  });

  const csvContent = "\uFEFF" + headers.join(',') + '\n' + rows.join('\n'); 
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `MacroWave_Options_Journal_${new Date().toISOString().split('T')[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
};

const triggerImport = () => {
  if (confirm('⚠️ 警告：匯入功能將會覆蓋/更新您現有的資料庫紀錄。請確認您上傳的是之前匯出的 JSON 備份檔。是否繼續？')) {
    fileInput.value.click();
  }
};

const handleImport = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const content = e.target.result;
      const importedData = JSON.parse(content);
      if (!Array.isArray(importedData)) throw new Error("資料格式錯誤，必須為陣列結構。");
      const { error } = await supabase.from('macrowave_options_journal').upsert(importedData);
      if (error) throw error;
      alert(`✅ 成功匯入並同步了 ${importedData.length} 筆交易紀錄至資料庫！`);
      await fetchTrades(); 
    } catch (err) {
      alert("❌ 匯入失敗，請確認檔案格式是否正確。\n錯誤訊息：" + err.message);
    }
    event.target.value = ''; 
  };
  reader.readAsText(file);
};

// ==========================================
// 📊 到期損益圖 (Payoff Diagram)
// ==========================================
const isChartModalOpen = ref(false);
const chartTradeData = ref(null);
let payoffChartInstance = null;

const openPayoffChart = async (trade) => {
  chartTradeData.value = trade;
  isChartModalOpen.value = true;
  await nextTick();
  renderPayoffChart(trade);
};

const closePayoffChart = () => {
  isChartModalOpen.value = false;
  if (payoffChartInstance) {
    payoffChartInstance.dispose();
    payoffChartInstance = null;
  }
};

const renderPayoffChart = (trade) => {
  const chartDom = document.getElementById('payoff-chart');
  if (!chartDom) return;
  
  payoffChartInstance = echarts.init(chartDom);
  const { strategy, strikes, entry_price, contracts } = trade;
  const multiplier = 100 * contracts;
  
  const { sP, lP, sC, lC, s, l } = getSafeStrikes(strategy, strikes);
  
  let minStrike = Infinity, maxStrike = -Infinity;

  if (strategy === 'bullPut') {
    minStrike = lP; maxStrike = sP;
  } else if (strategy === 'bearCall') {
    minStrike = sC; maxStrike = lC;
  } else if (strategy === 'ironCondor') {
    minStrike = lP; maxStrike = lC;
  } else if (strategy === 'vertical') { 
    minStrike = Math.min(s, l); maxStrike = Math.max(s, l);
  }

  const xData = [];
  const yData = [];
  
  const startPrice = minStrike * 0.85; 
  const endPrice = maxStrike * 1.15;   
  const step = (endPrice - startPrice) / 400; 

  for (let p = startPrice; p <= endPrice; p += step) {
    let pnl = 0;
    
    if (strategy === 'bullPut') {
      pnl = (entry_price - Math.max(sP - p, 0) + Math.max(lP - p, 0)) * multiplier;
    } else if (strategy === 'bearCall') {
      pnl = (entry_price - Math.max(p - sC, 0) + Math.max(p - lC, 0)) * multiplier;
    } else if (strategy === 'ironCondor') {
      pnl = (entry_price - Math.max(sP - p, 0) + Math.max(lP - p, 0) - Math.max(p - sC, 0) + Math.max(p - lC, 0)) * multiplier;
    } else if (strategy === 'vertical') {
      const isCallSpread = s < l;
      if (isCallSpread) pnl = (entry_price - Math.max(p - s, 0) + Math.max(p - l, 0)) * multiplier;
      else pnl = (entry_price - Math.max(s - p, 0) + Math.max(l - p, 0)) * multiplier;
    }
    
    xData.push(p.toFixed(2));
    yData.push(Number(pnl.toFixed(2)));
  }

  const option = {
    backgroundColor: 'transparent',
    title: {
      text: '背景 🟩 亮綠色 = 獲利區間   │   背景 🟥 淡紅色 = 虧損區間',
      left: 'center',
      top: 10,
      textStyle: { color: '#b2b5be', fontSize: 13, fontWeight: 'normal' }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params) => {
        const price = params[0].name;
        const pnl = Number(params[0].value);
        const color = pnl >= 0 ? '#26a69a' : '#ef5350';
        const status = pnl >= 0 ? '獲利' : '虧損';
        return `如果到期時股價為: <b>$${price}</b><br/>這筆交易將會: <span style="color:${color};font-weight:bold;font-size:16px;">${status} $${Math.abs(pnl).toFixed(2)}</span>`;
      }
    },
    xAxis: {
      type: 'category', 
      name: '到期時股價',
      nameLocation: 'middle',
      nameGap: 25,
      data: xData,
      axisLine: { lineStyle: { color: '#8c8f98' } },
      axisLabel: { formatter: (value, index) => { return index % 50 === 0 ? value : ''; } }
    },
    yAxis: {
      type: 'value',
      name: '總賺賠',
      axisLine: { lineStyle: { color: '#8c8f98' } },
      splitLine: { lineStyle: { color: '#2b2b43' } }
    },
    series: [
      {
        data: yData,
        type: 'line',
        symbol: 'none',
        itemStyle: { color: '#e0ac00' }, 
        lineStyle: { width: 3 },
        markArea: {
          silent: true,
          data: [
            [ { yAxis: 0, itemStyle: { color: 'rgba(38, 166, 154, 0.15)' } }, { yAxis: 'max' } ],
            [ { yAxis: 'min', itemStyle: { color: 'rgba(239, 83, 80, 0.15)' } }, { yAxis: 0 } ]
          ]
        },
        markLine: {
          silent: true,
          symbol: 'none',
          label: { position: 'end', formatter: '{b}', color: '#fff' },
          data: [ { yAxis: 0, lineStyle: { color: '#d1d4dc', type: 'solid', width: 2 }, name: '0' } ]
        },
        markPoint: {
          symbol: 'pin',
          symbolSize: 45,
          label: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
          data: [
            { type: 'max', name: 'Max', itemStyle: { color: '#26a69a' } },
            { type: 'min', name: 'Min', itemStyle: { color: '#ef5350' } }
          ]
        }
      }
    ]
  };

  payoffChartInstance.setOption(option);
};
</script>

<style scoped>
.journal-dashboard {
  background-color: #131722; color: #d1d4dc; padding: 16px;
  border-radius: 12px; font-family: -apple-system, sans-serif;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); margin: 0 auto;
}
.header { display: flex; flex-direction: column; gap: 12px; }
.title { font-size: 1.3rem; font-weight: 600; color: #fff; margin: 0; }

.export-actions { display: flex; gap: 8px; flex-wrap: wrap; width: 100%; }
.export-btn { 
  flex: 1; min-width: 100px; text-align: center;
  background: transparent; border: 1px solid #434651; color: #d1d4dc; 
  padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; 
  cursor: pointer; transition: all 0.2s; 
}
.export-btn:hover { background: #2a2e39; color: #fff; }
.export-btn.csv:hover { border-color: #00bcd4; color: #00bcd4; }
.export-btn.json:hover { border-color: #26a69a; color: #26a69a; }
.export-btn.import:hover { border-color: #e0ac00; color: #e0ac00; }

.view-toggles { display: flex; flex-direction: column; gap: 8px; width: 100%; border-bottom: 1px solid #2b2b43; padding-bottom: 16px; }
.view-btn { 
  width: 100%; padding: 12px; background-color: #1e222d; border: 1px solid #434651; 
  color: #8c8f98; border-radius: 6px; cursor: pointer; transition: 0.2s; font-weight: bold; font-size: 1rem;
}
.view-btn.active { background-color: #2962ff; color: #fff; border-color: #2962ff; }

.journal-layout { display: grid; grid-template-columns: 1fr; gap: 24px; }
.calendar-section { background-color: #1e222d; padding: 16px; border-radius: 8px; border: 1px solid #2b2b43; }
.calendar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.current-month { color: #fff; font-size: 1.1rem; margin: 0; }
.btn-icon { background: #2a2e39; border: 1px solid #434651; color: #d1d4dc; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
.calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; text-align: center; }
.weekday { color: #8c8f98; font-size: 0.8rem; margin-bottom: 4px; }
.calendar-day { 
  aspect-ratio: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  background-color: #2a2e39; border-radius: 6px; cursor: pointer; border: 1px solid transparent; 
}
.calendar-day.empty { background-color: transparent; cursor: default; }
.calendar-day.active { background-color: rgba(41, 98, 255, 0.2); border-color: #2962ff; color: #fff; font-weight: bold; }
.calendar-day.today .day-number { color: #26a69a; font-weight: bold; text-decoration: underline; }
.trade-dots { display: flex; gap: 2px; margin-top: 2px; }
.dot { width: 4px; height: 4px; background-color: #e0ac00; border-radius: 50%; }

.trade-card { background-color: #2a2e39; border-left: 4px solid #8c8f98; padding: 16px; border-radius: 6px; margin-bottom: 12px; }
.trade-card.open { border-color: #e0ac00; }
.trade-card.win { border-color: #26a69a; }
.trade-card.zero { border-color: #e0ac00; }
.trade-card.loss { border-color: #ef5350; }
.trade-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.strategy-badge { background-color: #1e222d; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; color: #8c8f98; }
.trade-detail { font-size: 0.9rem; color: #b2b5be; margin-bottom: 6px; word-break: break-all; }
.strikes-detail { background-color: #131722; padding: 8px; border-radius: 4px; margin: 8px 0; border-left: 3px solid #2962ff; }

/* 🌟 五色色彩系統 CSS 類別 */
.color-credit { color: #00bcd4 !important; } 
.color-debit { color: #ff9800 !important; }  
.color-zero { color: #e0ac00 !important; font-weight: bold; } 
.color-profit { color: #26a69a !important; } 
.color-loss { color: #ef5350 !important; }   

.risk-box { background: rgba(0,0,0,0.25); padding: 10px; border-radius: 4px; border: 1px solid #434651; }
.fs-7 { font-size: 0.8rem; }

.trade-card-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.action-btn { flex: 1; min-width: 80px; border: none; padding: 10px 8px; border-radius: 4px; font-size: 0.85rem; font-weight: bold; cursor: pointer; transition: opacity 0.2s; }
.action-btn:hover { opacity: 0.8; }
.view-btn { background-color: #e0ac00; color: #131722; } 
.edit-btn { background-color: #2962ff; color: #fff; }
.delete-btn { background-color: rgba(239, 83, 80, 0.2); color: #ef5350; }

.form-section { background-color: #1e222d; padding: 16px; border-radius: 8px; border: 1px solid #2b2b43; }
.form-group { margin-bottom: 14px; display: flex; flex-direction: column; gap: 4px; }
.form-group label { font-size: 0.85rem; color: #8c8f98; }
.dark-input { background-color: #2a2e39; border: 1px solid #434651; color: #fff; padding: 12px 10px; border-radius: 6px; outline: none; font-size: 1rem; }
.dark-input:focus { border-color: #2962ff; }
.strikes-grid { display: grid; grid-template-columns: 1fr; gap: 10px; }
.strikes-grid-4 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

.btn-add-fill { background: rgba(38, 166, 154, 0.1); color: #26a69a; border: 1px dashed #26a69a; border-radius: 4px; padding: 6px 12px; font-size: 0.8rem; cursor: pointer; transition: 0.2s; }
.btn-add-fill:hover { background: rgba(38, 166, 154, 0.2); }

.calc-preview { background-color: #131722; border: 1px dashed #434651; padding: 12px; border-radius: 8px; }
.calc-title { color: #e0ac00; margin-top: 0; font-size: 1.1rem; }
.submit-btn { background-color: #2962ff; color: #fff; border: none; padding: 14px; border-radius: 6px; font-weight: bold; font-size: 1rem; }
.cancel-btn { background-color: transparent; border: 1px solid #434651; color: #d1d4dc; padding: 14px; border-radius: 6px; font-size: 1rem; }

/* 模式二：結算總覽樣式 */
.summary-layout { display: flex; flex-direction: column; gap: 16px; }
.expiry-group-card { background-color: #1e222d; border: 1px solid #2b2b43; border-radius: 8px; padding: 16px; }
.expiry-header { border-bottom: 1px solid #2b2b43; padding-bottom: 12px; }
.summary-stats { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
.stat-item { background-color: #131722; padding: 12px; border-radius: 6px; border: 1px solid #434651; font-size: 1.1rem; font-weight: bold; }
.table-responsive { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.summary-table { width: 100%; min-width: 1100px; border-collapse: collapse; text-align: left; }
.summary-table th { color: #8c8f98; border-bottom: 1px solid #2b2b43; padding: 12px 8px; font-size: 0.85rem; }
.summary-table td { padding: 12px 8px; border-bottom: 1px solid #2b2b43; color: #d1d4dc; font-size: 0.9rem; }
.badge { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; }
.bg-primary { background-color: rgba(41, 98, 255, 0.2); color: #2962ff; border: 1px solid #2962ff; }
.bg-secondary { background-color: rgba(140, 143, 152, 0.2); color: #8c8f98; border: 1px solid #8c8f98; }
.action-icon-btn { background: #2a2e39; border: 1px solid #434651; border-radius: 4px; padding: 6px 8px; cursor: pointer; transition: 0.2s; font-size: 1.1rem; }
.action-icon-btn:hover { background: #363a45; border-color: #8c8f98; }

/* Modal 樣式 */
.chart-modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background-color: rgba(0, 0, 0, 0.9); z-index: 9999;
  display: flex; align-items: center; justify-content: center; padding: 10px;
}
.chart-modal-content {
  background-color: #131722; border: 1px solid #2b2b43; border-radius: 10px;
  width: 100%; max-width: 900px; padding: 16px;
}
.form-modal-content {
  background-color: #1e222d; border: 1px solid #2b2b43; border-radius: 12px;
  width: 90%; max-width: 600px; padding: 24px; box-shadow: 0 12px 48px rgba(0,0,0,0.5);
  max-height: 90vh; overflow-y: auto;
}
.close-btn { background: none; border: none; color: #8c8f98; font-size: 1.5rem; cursor: pointer; }
.close-btn:hover { color: #fff; }

@media (min-width: 768px) {
  .journal-dashboard { padding: 24px; }
  .header { flex-direction: row; }
  .title { font-size: 1.5rem; }
  .export-actions { width: auto; flex-wrap: nowrap; }
  .export-btn { flex: initial; }
  .view-toggles { flex-direction: row; }
  .view-btn { width: auto; }
  .journal-layout { grid-template-columns: 1fr 1fr; }
  .strikes-grid { grid-template-columns: 1fr 1fr; }
  .strikes-grid-4 { grid-template-columns: 1fr 1fr 1fr 1fr; }
  .summary-stats { flex-direction: row; }
  .stat-item { flex: 1; }
  .chart-modal-content { padding: 24px; }
}
</style>
