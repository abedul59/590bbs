import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const read = path => readFile(new URL(`../${path}`, import.meta.url), 'utf8')

test('announcement creation can create a publicly editable Google presentation', async () => {
  const [endpoint, helper, quickCreate, adminPublic, config] = await Promise.all([
    read('server/api/google-slides/create.post.ts'),
    read('server/utils/googleSlides.ts'),
    read('components/PublicQuickCreate.vue'),
    read('components/AdminPublic.vue'),
    read('nuxt.config.ts')
  ])

  assert.match(endpoint, /assertAdminPassword/)
  assert.match(endpoint, /createEditableGooglePresentation/)
  assert.match(helper, /slides\.googleapis\.com\/v1\/presentations/)
  assert.match(helper, /drive\/v3\/files\/.*permissions/)
  assert.match(helper, /type: 'anyone'/)
  assert.match(helper, /role: 'writer'/)
  assert.match(helper, /allowFileDiscovery: false/)
  assert.match(quickCreate, /\/api\/google-slides\/create/)
  assert.match(adminPublic, /\/api\/google-slides\/create/)
  assert.match(config, /googleRefreshToken/)
  assert.doesNotMatch(config, /public:\s*{[^}]*googleRefreshToken/s)
})

test('Google OAuth secrets stay server-side and are documented', async () => {
  const [readme, config] = await Promise.all([read('README.md'), read('nuxt.config.ts')])

  assert.match(readme, /GOOGLE_CLIENT_ID/)
  assert.match(readme, /GOOGLE_CLIENT_SECRET/)
  assert.match(readme, /GOOGLE_REFRESH_TOKEN/)
  assert.match(readme, /知道連結的任何人可編輯/)
  assert.match(config, /process\.env\.GOOGLE_CLIENT_SECRET/)
})
