export const MACROWAVE_SOURCE_TYPES = ['Render 自動同步', 'GUI JSON 手動上傳'] as const

export type MacrowaveContent = Record<string, unknown> & {
  total_score?: number | string
  raw_indicators?: Record<string, unknown>
  mark17?: unknown[]
  mark17_details?: unknown[]
}

export function isMacrowaveContent(value: unknown): value is MacrowaveContent {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false

  const content = value as MacrowaveContent
  const score = Number(content.total_score)
  const hasScore = Number.isFinite(score) && score >= 0 && score <= 15
  const hasRawIndicators = Boolean(
    content.raw_indicators
    && typeof content.raw_indicators === 'object'
    && !Array.isArray(content.raw_indicators)
  )
  // 舊版資料可能尚未輸出 Mark 17 明細，但一定具有總分與總經原始指標。
  return hasScore && hasRawIndicators
}

export function isCompleteMacrowaveContent(value: unknown): value is MacrowaveContent {
  if (!isMacrowaveContent(value)) return false
  return Array.isArray(value.mark17) || Array.isArray(value.mark17_details)
}
