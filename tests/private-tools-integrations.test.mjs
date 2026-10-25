import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const read = path => readFile(new URL(`../${path}`, import.meta.url), 'utf8')

test('hidden console exposes imported tools with refresh-stable query views', async () => {
  const page = await read('pages/macrowave.vue')

  assert.match(page, /selectedView === 'twstocktracker'/)
  assert.match(page, /selectedView === 'moneydam'/)
  assert.match(page, /TwstocktrackerDashboard/)
  assert.match(page, /MoneydamDashboard/)
  assert.match(page, /selectedView === 'bengo'/)
  assert.match(page, /selectedView === 'media-tools'/)
  assert.match(page, /BengoDashboard/)
  assert.match(page, /MediaToolsDashboard/)
})

test('Bengo uses namespaced APIs, callback URL, and portable storage fallback', async () => {
  const [page, dataApi, uploadApi, triggerApi] = await Promise.all([
    read('components/bengo/Dashboard.vue'),
    read('server/api/bengo/data.get.ts'),
    read('server/api/bengo/upload.post.ts'),
    read('server/api/bengo/trigger.post.ts')
  ])

  assert.match(page, /\/api\/bengo\/data/)
  assert.match(page, /\/api\/bengo\/upload/)
  assert.match(page, /\/api\/bengo\/trigger/)
  assert.match(dataApi, /Bengo stock data/)
  assert.match(uploadApi, /macrowave_dashboard_data/)
  assert.match(triggerApi, /\/api\/bengo\/upload/)
})

test('media tools preserve direct large-file conversion and cutting endpoints', async () => {
  const page = await read('components/media-tools/Dashboard.vue')

  assert.match(page, /3gp2mp3-api\.hf\.space/)
  assert.match(page, /\/api\/convert/)
  assert.match(page, /\/api\/cut/)
  assert.match(page, /URL\.revokeObjectURL/)
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
