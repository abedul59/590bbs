import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const read = path => readFile(new URL(`../${path}`, import.meta.url), 'utf8')

test('MacroWave APIs isolate shared-table records by source and payload shape', async () => {
  const [latest, historyList, history, upload, validator] = await Promise.all([
    read('server/api/macrowave/latest.get.ts'),
    read('server/api/macrowave/history-list.get.ts'),
    read('server/api/macrowave/history.get.ts'),
    read('server/api/macrowave/upload.post.ts'),
    read('server/utils/macrowaveRecords.ts')
  ])

  for (const source of [latest, historyList, history]) {
    assert.match(source, /MACROWAVE_SOURCE_TYPES/)
    assert.match(source, /\.in\('source_type'/)
    assert.match(source, /isMacrowaveContent/)
  }
  assert.match(upload, /isCompleteMacrowaveContent\(body\)/)
  assert.match(validator, /Render 自動同步/)
  assert.match(validator, /GUI JSON 手動上傳/)
  assert.match(validator, /isCompleteMacrowaveContent/)
  assert.match(validator, /value\.mark17/)
  assert.doesNotMatch(latest, /\.limit\(1\)\s*\.single\(\)/)
})

test('MacroWave dashboard clears invalid data instead of rendering another tool payload', async () => {
  const dashboard = await read('components/macrowave/TabDashboard.vue')

  assert.match(dashboard, /res\.data\?\.content/)
  assert.match(dashboard, /rawResponseData\.value = null/)
  assert.match(dashboard, /loadError/)
})
