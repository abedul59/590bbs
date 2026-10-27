const PLACEHOLDER_KEYS = new Set([
  '',
  'your_fred_api_key',
  'your fred api key',
  'fred_api_key',
  '請填入您的 fred api key'
])

export function normalizeFredApiKey(value: unknown) {
  const key = String(value ?? '').trim()
  if (!key || PLACEHOLDER_KEYS.has(key.toLowerCase())) return ''
  return key
}

export function resolveFredApiKey(event?: any) {
  const runtimeConfig = useRuntimeConfig(event)
  const candidates = [
    runtimeConfig.fredApiKey,
    process.env.NUXT_FRED_API_KEY,
    process.env.FRED_API_KEY,
    process.env.FRED_KEY,
    process.env.FRED_API_TOKEN
  ]
  return candidates.map(normalizeFredApiKey).find(Boolean) || ''
}

export function fredConfigurationHelp() {
  return '請在 Vercel Production、Preview、Development 環境設定 FRED_API_KEY（或 NUXT_FRED_API_KEY），然後重新部署。'
}
