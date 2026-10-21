import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { createServer } from 'node:http'
import test from 'node:test'

const runMigration = (environment) => new Promise((resolve, reject) => {
  const child = spawn(process.execPath, ['scripts/migrate-tlogs-shjhs.mjs'], {
    cwd: process.cwd(),
    env: { ...process.env, ...environment },
    stdio: ['ignore', 'pipe', 'pipe']
  })
  let stdout = ''
  let stderr = ''
  child.stdout.on('data', (chunk) => { stdout += chunk })
  child.stderr.on('data', (chunk) => { stderr += chunk })
  child.on('error', reject)
  child.on('close', (code) => resolve({ code, stdout, stderr }))
})

test('transfers both tables and gives legacy evidence IDs a stable prefix', async (context) => {
  const writes = new Map()
  const sourceRows = {
    counseling_logs: [{ id: '4e640c9a-e456-4b94-9589-078ae3123dfa', record_date: '2026-10-20', content: 'test', updated_at: '2026-10-20T00:00:00Z' }],
    evidence_logs: [{ id: 7, log_date: '2026-10-20', title: 'audio', message_id: 99, created_at: '2026-10-20T00:00:00Z' }]
  }

  const server = createServer((request, response) => {
    const url = new URL(request.url, 'http://localhost')
    const table = url.pathname.split('/').at(-1)
    if (request.method === 'GET' && url.pathname.startsWith('/source/')) {
      response.setHeader('Content-Type', 'application/json')
      response.end(JSON.stringify(sourceRows[table]))
      return
    }
    if (request.method === 'POST' && url.pathname.startsWith('/target/')) {
      let body = ''
      request.on('data', (chunk) => { body += chunk })
      request.on('end', () => {
        writes.set(table, JSON.parse(body))
        response.statusCode = 201
        response.end()
      })
      return
    }
    response.statusCode = 404
    response.end()
  })

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve))
  context.after(() => server.close())
  const { port } = server.address()
  const result = await runMigration({
    SOURCE_SUPABASE_URL: `http://127.0.0.1:${port}/source`,
    SOURCE_SUPABASE_KEY: 'source-test-key',
    TARGET_SUPABASE_URL: `http://127.0.0.1:${port}/target`,
    TARGET_SUPABASE_KEY: 'target-test-key'
  })

  assert.equal(result.code, 0, result.stderr)
  assert.deepEqual(writes.get('counseling_logs'), sourceRows.counseling_logs)
  assert.equal(writes.get('evidence_logs')[0].id, 'legacy:7')
  assert.match(result.stdout, /Migration complete/)
})
