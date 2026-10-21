import { waitUntil } from '@vercel/functions'

const renderTriggerUrl = 'https://five90bbs-render-cron-api.onrender.com/run'

const wakeRender = async () => {
  try {
    const response = await fetch(renderTriggerUrl, {
      method: 'GET',
      headers: { 'User-Agent': '590bbs-vercel-cron-bridge/1.0' },
      cache: 'no-store',
      signal: AbortSignal.timeout(50_000),
    })
    // The bridge never forwards Render response data to cron-job.org.
    await response.body?.cancel()
  } catch (error) {
    // The initial request is often enough to start a sleeping free instance.
    // Log only the error type so URLs and response bodies never enter logs.
    console.error('Render cron wake failed:', error instanceof Error ? error.name : 'UnknownError')
  }
}

export default defineEventHandler((event) => {
  const task = wakeRender()

  try {
    // Vercel keeps the function alive after the empty response is sent.
    waitUntil(task)
  } catch {
    // Local/Nitro runtimes have no Vercel request context. The request has
    // already started, so keep it detached for local development.
    void task
  }

  setResponseStatus(event, 204)
  setResponseHeader(event, 'Cache-Control', 'no-store, max-age=0')
  setResponseHeader(event, 'Content-Length', '0')
  return null
})
