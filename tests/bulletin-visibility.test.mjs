import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'

const read = path => readFile(new URL(`../${path}`, import.meta.url), 'utf8')

test('admin can hide bulletins while the homepage excludes them', async () => {
  const [visibility, admin, homepage] = await Promise.all([
    read('utils/bulletinVisibility.ts'),
    read('components/AdminPublic.vue'),
    read('pages/index.vue')
  ])

  assert.match(visibility, /BULLETIN_HIDDEN_MARKER/)
  assert.match(visibility, /setBulletinHidden/)
  assert.match(admin, /togglePostVisibility/)
  assert.match(admin, /恢復顯示/)
  assert.match(admin, /已從首頁隱藏/)
  assert.match(homepage, /!isBulletinHidden\(b\)/)
  assert.match(homepage, /getVisibleBulletinLinks\(item\)/)
})
