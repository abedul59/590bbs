const requiredVariables = [
  'SOURCE_SUPABASE_URL',
  'SOURCE_SUPABASE_KEY',
  'TARGET_SUPABASE_URL',
  'TARGET_SUPABASE_KEY'
]

const missing = requiredVariables.filter((name) => !process.env[name])
if (missing.length > 0) {
  console.error(`Missing environment variables: ${missing.join(', ')}`)
  process.exit(1)
}

const source = {
  url: process.env.SOURCE_SUPABASE_URL.replace(/\/$/, ''),
  key: process.env.SOURCE_SUPABASE_KEY
}
const target = {
  url: process.env.TARGET_SUPABASE_URL.replace(/\/$/, ''),
  key: process.env.TARGET_SUPABASE_KEY
}
const dryRun = process.argv.includes('--dry-run')
const pageSize = 1000
const batchSize = 200

const headers = (key, extra = {}) => ({
  apikey: key,
  Authorization: `Bearer ${key}`,
  ...extra
})

const request = async (url, options = {}) => {
  const response = await fetch(url, options)
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(`${response.status} ${response.statusText}: ${detail}`)
  }
  const body = await response.text()
  return body ? JSON.parse(body) : null
}

const readTable = async (table, orderColumn) => {
  const rows = []
  for (let offset = 0; ; offset += pageSize) {
    const params = new URLSearchParams({
      select: '*',
      order: `${orderColumn}.asc`,
      offset: String(offset),
      limit: String(pageSize)
    })
    const page = await request(`${source.url}/rest/v1/${table}?${params}`, {
      headers: headers(source.key)
    })
    rows.push(...page)
    if (page.length < pageSize) return rows
  }
}

const upsertTable = async (table, rows) => {
  for (let index = 0; index < rows.length; index += batchSize) {
    await request(`${target.url}/rest/v1/${table}?on_conflict=id`, {
      method: 'POST',
      headers: headers(target.key, {
        'Content-Type': 'application/json',
        Prefer: 'resolution=merge-duplicates,return=minimal'
      }),
      body: JSON.stringify(rows.slice(index, index + batchSize))
    })
  }
}

const tables = [
  { name: 'counseling_logs', order: 'updated_at' },
  { name: 'evidence_logs', order: 'id' }
]

for (const table of tables) {
  const sourceRows = await readTable(table.name, table.order)
  const rows = table.name === 'evidence_logs'
    ? sourceRows.map((row) => ({ ...row, id: `legacy:${row.id}` }))
    : sourceRows
  console.log(`${table.name}: found ${rows.length} source rows`)
  if (!dryRun) {
    await upsertTable(table.name, rows)
    console.log(`${table.name}: transferred ${rows.length} rows`)
  }
}

console.log(dryRun ? 'Dry run complete; target was not changed.' : 'Migration complete.')
