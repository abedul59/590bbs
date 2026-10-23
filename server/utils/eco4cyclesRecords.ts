export interface Eco4CyclesRecord {
  date: string
  verdict: string
  strategy: string
  scores: Record<string, unknown>
  details: Record<string, unknown>
  raw_data: Record<string, unknown>
}

export async function readEco4CyclesSnapshot(): Promise<Eco4CyclesRecord[]> {
  const value = await useStorage('assets:server').getItem<Eco4CyclesRecord[]>('eco4cycles-records.json')
  return Array.isArray(value) ? value : []
}
