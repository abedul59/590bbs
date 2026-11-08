type GoogleTokenResponse = { access_token?: string }
type GooglePresentationResponse = { presentationId?: string }

const configurationError = () => createError({
  statusCode: 503,
  message: 'Google 簡報尚未設定，請先在 Vercel 設定 GOOGLE_CLIENT_ID、GOOGLE_CLIENT_SECRET 與 GOOGLE_REFRESH_TOKEN。'
})

const getAccessToken = async (event: Parameters<typeof useRuntimeConfig>[0]) => {
  const config = useRuntimeConfig(event)
  const clientId = String(config.googleClientId || '').trim()
  const clientSecret = String(config.googleClientSecret || '').trim()
  const refreshToken = String(config.googleRefreshToken || '').trim()

  if (!clientId || !clientSecret || !refreshToken) throw configurationError()

  try {
    const response = await $fetch<GoogleTokenResponse>('https://oauth2.googleapis.com/token', {
      method: 'POST',
      body: new URLSearchParams({
        client_id: clientId,
        client_secret: clientSecret,
        refresh_token: refreshToken,
        grant_type: 'refresh_token'
      })
    })
    if (!response.access_token) throw new Error('Google token response did not contain access_token')
    return response.access_token
  } catch (error) {
    console.error('Google OAuth token refresh failed', error)
    throw createError({
      statusCode: 502,
      message: '無法取得 Google 授權，請檢查 OAuth refresh token 是否仍有效。'
    })
  }
}

export const createEditableGooglePresentation = async (
  event: Parameters<typeof useRuntimeConfig>[0],
  requestedTitle: string
) => {
  const title = requestedTitle.trim().slice(0, 180)
  if (!title) throw createError({ statusCode: 400, message: '簡報標題不能為空。' })

  const accessToken = await getAccessToken(event)
  const headers = { Authorization: `Bearer ${accessToken}` }
  let presentationId = ''

  try {
    const presentation = await $fetch<GooglePresentationResponse>('https://slides.googleapis.com/v1/presentations', {
      method: 'POST',
      headers,
      body: { title }
    })
    presentationId = String(presentation.presentationId || '')
    if (!presentationId) throw new Error('Google Slides response did not contain presentationId')

    await $fetch(`https://www.googleapis.com/drive/v3/files/${encodeURIComponent(presentationId)}/permissions`, {
      method: 'POST',
      headers,
      query: { supportsAllDrives: 'true' },
      body: { type: 'anyone', role: 'writer', allowFileDiscovery: false }
    })

    return {
      presentationId,
      title,
      editUrl: `https://docs.google.com/presentation/d/${presentationId}/edit`,
      permission: 'anyone-with-link-writer'
    }
  } catch (error) {
    console.error('Google presentation creation failed', error)
    if (presentationId) {
      await $fetch(`https://www.googleapis.com/drive/v3/files/${encodeURIComponent(presentationId)}`, {
        method: 'DELETE', headers
      }).catch(cleanupError => console.error('Google presentation cleanup failed', cleanupError))
    }
    throw createError({
      statusCode: 502,
      message: 'Google 簡報建立失敗。請確認 Drive／Slides API 已啟用，而且帳號允許「知道連結的任何人可編輯」。'
    })
  }
}
