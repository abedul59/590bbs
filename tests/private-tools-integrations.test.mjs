import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const read = path => readFile(new URL(`../${path}`, import.meta.url), 'utf8')

test('hidden console exposes both imported tools with refresh-stable query views', async () => {
  const page = await read('pages/macrowave.vue')

  assert.match(page, /selectedView === 'twstocktracker'/)
  assert.match(page, /selectedView === 'moneydam'/)
  assert.match(page, /TwstocktrackerDashboard/)
  assert.match(page, /MoneydamDashboard/)
})

test('imported tools use namespaced APIs and portable database fallbacks', async () => {
  const [trackerTrigger, moneydamTrigger] = await Promise.all([
    read('server/api/twstocktracker/trigger.post.ts'),
    read('server/api/moneydam/trigger.post.ts')
  ])

  assert.match(trackerTrigger, /Twstock tracker record/)
  assert.match(moneydamTrigger, /Moneydam analysis/)
  assert.match(trackerTrigger, /macrowave_dashboard_data/)
  assert.match(moneydamTrigger, /macrowave_dashboard_data/)
})
