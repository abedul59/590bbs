import { assertAdminPassword } from '../../utils/adminPassword'
import { createEditableGooglePresentation } from '../../utils/googleSlides'

export default defineEventHandler(async (event) => {
  assertAdminPassword(event)
  const body = await readBody<{ title?: string }>(event)
  const title = String(body?.title || '').trim()
  if (!title) throw createError({ statusCode: 400, message: '公告標題不能為空。' })
  return createEditableGooglePresentation(event, `${title}｜公告簡報`)
})
