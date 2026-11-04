import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const read = path => readFile(new URL(`../${path}`, import.meta.url), 'utf8')

test('cron bridge uses the active 590bbs deployment and returns a tiny queued response', async () => {
  const [config, admin, endpoint, readme] = await Promise.all([
    read('nuxt.config.ts'),
    read('components/AdminCron.vue'),
    read('server/api/cron-render.get.ts'),
    read('README.md')
  ])

  assert.match(config, /https:\/\/590bbs\.vercel\.app\/api\/cron-render/)
  assert.match(config, /NUXT_PUBLIC_CRON_BRIDGE_URL/)
  assert.doesNotMatch(admin, /shjhs-class-system\.vercel\.app/)
  assert.match(admin, /runtimeConfig\.public\.cronBridgeUrl/)
  assert.match(admin, /testCronBridge/)
  assert.match(endpoint, /setResponseStatus\(event, 202\)/)
  assert.match(endpoint, /status: 'queued'/)
  assert.match(endpoint, /waitUntil\(task\)/)
  assert.match(readme, /https:\/\/590bbs\.vercel\.app\/api\/cron-render/)
})
