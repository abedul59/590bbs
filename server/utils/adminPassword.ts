import { getTodayPassword } from '../../utils/auth'

export const assertAdminPassword = (event: Parameters<typeof getHeader>[0]) => {
  const suppliedPassword = getHeader(event, 'x-admin-password') || ''

  if (!suppliedPassword || suppliedPassword !== getTodayPassword()) {
    throw createError({
      statusCode: 401,
      message: '管理員驗證已失效，請重新登入後再試。'
    })
  }
}
