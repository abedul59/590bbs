import { createClient } from '@supabase/supabase-js'

// 抓取您環境變數中的 Supabase 憑證 (與您原本專案設定相同)
const supabaseUrl = process.env.SUPABASE_URL || ''
const supabaseKey = process.env.SUPABASE_KEY || ''
const supabase = createClient(supabaseUrl, supabaseKey)

export default defineEventHandler(async (event) => {
  const method = event.node.req.method

  // [讀取] 所有筆記
  if (method === 'GET') {
    const { data, error } = await supabase.from('macrowave_bulletins').select('*').order('created_at', { ascending: false })
    if (error) return { success: false, message: error.message }
    return { success: true, data }
  }

  // [新增/修改] 筆記
  if (method === 'POST') {
    const body = await readBody(event)
    if (body.id) {
        // 有 ID 代表是編輯更新
        const { error } = await supabase.from('macrowave_bulletins').update({
            title: body.title,
            content: body.content,
            urls: body.urls
        }).eq('id', body.id)
        if (error) return { success: false, message: error.message }
    } else {
        // 沒 ID 代表是全新建立
        const { error } = await supabase.from('macrowave_bulletins').insert({
            title: body.title,
            content: body.content,
            urls: body.urls
        })
        if (error) return { success: false, message: error.message }
    }
    return { success: true }
  }

  // [刪除] 筆記
  if (method === 'DELETE') {
    const query = getQuery(event)
    if (!query.id) return { success: false, message: '缺少 ID' }
    const { error } = await supabase.from('macrowave_bulletins').delete().eq('id', query.id)
    if (error) return { success: false, message: error.message }
    return { success: true }
  }
})
