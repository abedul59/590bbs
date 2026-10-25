<template>
  <div class="media-page">
    <div class="media-shell">
      <div class="tool-tabs">
        <button :class="{ active: activeTool === 'convert' }" @click="activeTool = 'convert'">🎵 3GP 轉 MP3</button>
        <button :class="{ active: activeTool === 'cut' }" @click="activeTool = 'cut'">✂️ 音訊切割</button>
      </div>

      <section v-if="activeTool === 'convert'" class="panel">
        <header><h2>3GP／3GPP 轉 MP3</h2><p>檔案直接傳送至雲端轉檔引擎，不經過 590bbs 或 Vercel 儲存。</p></header>
        <label class="drop-zone" @dragover.prevent @drop.prevent="handleDrop">
          <span class="drop-icon">☁️</span>
          <strong>選擇多個檔案，或拖曳至此</strong>
          <small>支援 .3gp、.3gpp；建議單檔不超過 500 MB</small>
          <input type="file" accept=".3gp,.3gpp,audio/3gpp,video/3gpp" multiple @change="handleConvertFiles">
        </label>

        <div class="options">
          <strong>✨ 音訊優化</strong>
          <label><input v-model="optimization.noiseReduction" type="checkbox"> 消除背景底噪</label>
          <label><input v-model="optimization.silenceRemoval" type="checkbox"> 自動移除無聲空白</label>
          <label><input v-model="optimization.normalize" type="checkbox"> 音量平穩化</label>
        </div>

        <div v-if="queue.length" class="queue">
          <article v-for="item in queue" :key="item.id" class="queue-item">
            <div class="file-line"><div><strong>{{ item.name }}</strong><small>{{ item.size }}</small></div><span :class="`status-${item.status}`">{{ statusText(item) }}</span></div>
            <div class="progress"><span :style="{ width: `${item.progress}%` }"></span></div>
            <a v-if="item.status === 'done'" :href="item.url" :download="downloadName(item.name)" class="download">下載 MP3</a>
            <button v-if="item.status === 'error'" class="retry" @click="retryItem(item)">重試</button>
            <p v-if="item.error" class="error">{{ item.error }}</p>
          </article>
        </div>
      </section>

      <section v-else class="panel">
        <header><h2>MP3／音訊線上切割</h2><p>可精準擷取指定範圍，或依固定秒數分割並下載 ZIP。</p></header>
        <label class="file-picker">
          <strong>步驟一：選擇音訊或影片檔</strong>
          <input type="file" accept="audio/*,video/*,.3gp,.3gpp,.m4a,.mp3" @change="loadCutFile">
        </label>
        <audio v-if="previewUrl" ref="audioPlayer" :src="previewUrl" controls class="audio-player"></audio>

        <div v-if="cutFile" class="cut-controls">
          <strong>步驟二：設定切割方式</strong>
          <div class="mode-row">
            <label><input v-model="cutMode" type="radio" value="segment"> 精準擷取</label>
            <label><input v-model="cutMode" type="radio" value="interval"> 等分切割</label>
          </div>
          <div v-if="cutMode === 'segment'" class="time-grid">
            <label>起點（秒）<span><input v-model.number="startTime" type="number" min="0" step="0.1"><button @click="setCurrentTime('start')">目前播放</button></span></label>
            <label>終點（秒）<span><input v-model.number="endTime" type="number" min="0" step="0.1"><button @click="setCurrentTime('end')">目前播放</button></span></label>
          </div>
          <label v-else class="interval-field">每段秒數<input v-model.number="intervalSeconds" type="number" min="1" step="1"></label>
          <button class="process" :disabled="cutting" @click="processCut">{{ cutting ? '雲端處理中…' : '🚀 開始切割' }}</button>
          <p v-if="cutError" class="error">{{ cutError }}</p>
        </div>

        <div v-if="cutDownloadUrl" class="finished"><span>✅ 處理完成</span><a :href="cutDownloadUrl" :download="cutDownloadName">下載 {{ cutDownloadName }}</a></div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, reactive, ref } from 'vue'

const HF_BASE_URL = 'https://lawxstudents168-3gp2mp3-api.hf.space'
const activeTool = ref('convert')
const queue = ref([])
const optimization = reactive({ noiseReduction: false, silenceRemoval: false, normalize: false })
let queueRunning = false

const addFiles = files => {
  Array.from(files || []).filter(file => /\.3gpp?$/i.test(file.name)).forEach(file => {
    queue.value.push({
      id: `${Date.now()}-${crypto.randomUUID?.() || Math.random().toString(36).slice(2)}`,
      name: file.name,
      size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
      rawFile: file,
      status: 'idle', progress: 0, url: '', error: ''
    })
  })
  processQueue()
}

const handleConvertFiles = event => { addFiles(event.target.files); event.target.value = '' }
const handleDrop = event => addFiles(event.dataTransfer?.files)
const downloadName = name => name.replace(/\.3gpp?$/i, '.mp3')
const statusText = item => ({ idle: '等待中', processing: `上傳與轉檔 ${item.progress}%`, done: '完成', error: '失敗' }[item.status])

const convertItem = async item => {
  const timer = setInterval(() => { if (item.progress < 94) item.progress = Math.min(94, item.progress + Math.floor(Math.random() * 5) + 1) }, 1000)
  const formData = new FormData()
  formData.append('file', item.rawFile, 'input.3gp')
  formData.append('options', JSON.stringify(optimization))
  try {
    const response = await fetch(`${HF_BASE_URL}/api/convert`, { method: 'POST', body: formData })
    if (!response.ok) throw new Error(`雲端引擎回應 ${response.status}：${(await response.text()).slice(0, 300)}`)
    if (item.url) URL.revokeObjectURL(item.url)
    item.url = URL.createObjectURL(await response.blob())
  } finally {
    clearInterval(timer)
  }
}

const processQueue = async () => {
  if (queueRunning) return
  queueRunning = true
  for (const item of queue.value) {
    if (item.status !== 'idle') continue
    item.status = 'processing'; item.progress = 1; item.error = ''
    try {
      await convertItem(item)
      item.status = 'done'; item.progress = 100
    } catch (error) {
      item.status = 'error'; item.error = error.message || String(error)
    }
  }
  queueRunning = false
}

const retryItem = item => { item.status = 'idle'; item.progress = 0; processQueue() }

const cutFile = ref(null)
const previewUrl = ref('')
const audioPlayer = ref(null)
const cutMode = ref('segment')
const startTime = ref(0)
const endTime = ref(0)
const intervalSeconds = ref(30)
const cutting = ref(false)
const cutError = ref('')
const cutDownloadUrl = ref('')
const cutDownloadName = ref('cut_audio.mp3')

const revoke = value => { if (value) URL.revokeObjectURL(value) }
const loadCutFile = event => {
  const file = event.target.files?.[0]
  if (!file) return
  cutFile.value = file
  revoke(previewUrl.value); previewUrl.value = URL.createObjectURL(file)
  revoke(cutDownloadUrl.value); cutDownloadUrl.value = ''
  startTime.value = 0; endTime.value = 0; cutError.value = ''
}
const setCurrentTime = target => {
  const value = Number((audioPlayer.value?.currentTime || 0).toFixed(1))
  if (target === 'start') startTime.value = value
  else endTime.value = value
}

const processCut = async () => {
  if (!cutFile.value) return
  if (cutMode.value === 'segment' && Number(endTime.value) <= Number(startTime.value)) {
    cutError.value = '終點時間必須大於起點時間。'; return
  }
  if (cutMode.value === 'interval' && Number(intervalSeconds.value) <= 0) {
    cutError.value = '切割間隔必須大於 0。'; return
  }
  cutting.value = true; cutError.value = ''; revoke(cutDownloadUrl.value); cutDownloadUrl.value = ''
  const formData = new FormData()
  formData.append('file', cutFile.value)
  formData.append('mode', cutMode.value)
  if (cutMode.value === 'segment') {
    formData.append('start', String(startTime.value)); formData.append('end', String(endTime.value))
  } else formData.append('interval', String(intervalSeconds.value))
  try {
    const response = await fetch(`${HF_BASE_URL}/api/cut`, { method: 'POST', body: formData })
    if (!response.ok) throw new Error(`雲端引擎回應 ${response.status}：${(await response.text()).slice(0, 300)}`)
    const disposition = response.headers.get('Content-Disposition') || ''
    const filename = disposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';]+)/i)?.[1]
    cutDownloadName.value = filename ? decodeURIComponent(filename) : (cutMode.value === 'interval' ? 'segments.zip' : 'cut_audio.mp3')
    cutDownloadUrl.value = URL.createObjectURL(await response.blob())
  } catch (error) {
    cutError.value = `處理失敗：${error.message || error}`
  } finally {
    cutting.value = false
  }
}

onBeforeUnmount(() => {
  queue.value.forEach(item => revoke(item.url))
  revoke(previewUrl.value); revoke(cutDownloadUrl.value)
})
</script>

<style scoped>
.media-page { min-height: calc(100vh - 62px); padding: 1.5rem; background: #f8fafc; }.media-shell { width: min(900px, 100%); margin: auto; }
.tool-tabs { display: flex; gap: .65rem; margin-bottom: 1rem; }.tool-tabs button { flex: 1; padding: .9rem; border: 0; border-radius: .8rem; color: #475569; background: #e2e8f0; font-weight: 900; }.tool-tabs button.active { color: #fff; background: #4f46e5; }
.panel { padding: clamp(1rem, 3vw, 2rem); border-radius: 1.1rem; background: #fff; box-shadow: 0 12px 35px #0f172a14; }.panel header { text-align: center; }.panel header h2 { margin: 0 0 .5rem; font-weight: 900; }.panel header p { color: #64748b; }
.drop-zone { display: flex; flex-direction: column; align-items: center; gap: .5rem; margin: 1.5rem 0; padding: 2.5rem 1rem; border: 2px dashed #a5b4fc; border-radius: 1rem; background: #eef2ff; cursor: pointer; }.drop-zone input { margin-top: .7rem; }.drop-icon { font-size: 2.5rem; }.drop-zone small { color: #64748b; }
.options { display: flex; flex-wrap: wrap; gap: 1rem; padding: 1rem; border: 1px solid #e2e8f0; border-radius: .8rem; }.options strong { flex-basis: 100%; }.options label, .mode-row label { display: flex; align-items: center; gap: .4rem; }
.queue { margin-top: 1rem; }.queue-item { padding: 1rem 0; border-bottom: 1px solid #e2e8f0; }.file-line { display: flex; justify-content: space-between; gap: 1rem; }.file-line div { min-width: 0; }.file-line strong, .file-line small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.file-line small { color: #64748b; }
.progress { height: .55rem; margin: .65rem 0; overflow: hidden; border-radius: 999px; background: #e2e8f0; }.progress span { display: block; height: 100%; background: #4f46e5; transition: width .3s; }.status-done { color: #15803d; }.status-error, .error { color: #b91c1c; }.download, .finished a { display: inline-block; padding: .45rem .75rem; border-radius: .5rem; color: #fff; background: #16a34a; font-weight: 800; text-decoration: none; }.retry { border: 0; border-radius: .5rem; padding: .45rem .75rem; color: #fff; background: #dc2626; }
.file-picker { display: grid; gap: .8rem; margin: 1.5rem 0; padding: 1rem; border: 1px solid #e2e8f0; border-radius: .8rem; }.audio-player { width: 100%; margin-bottom: 1.5rem; }.cut-controls { display: grid; gap: 1rem; padding: 1.25rem; border-radius: .8rem; background: #f8fafc; }.mode-row, .time-grid { display: flex; gap: 1rem; }.time-grid > label { flex: 1; }.time-grid span { display: flex; gap: .5rem; margin-top: .4rem; }.time-grid input, .interval-field input { width: 100%; padding: .55rem; border: 1px solid #cbd5e1; border-radius: .45rem; }.time-grid button { white-space: nowrap; border: 0; border-radius: .45rem; }.interval-field { display: grid; gap: .4rem; }.process { padding: .8rem; border: 0; border-radius: .6rem; color: #fff; background: #4f46e5; font-weight: 900; }.process:disabled { opacity: .55; }.finished { display: flex; align-items: center; justify-content: space-between; margin-top: 1rem; padding: 1rem; border-radius: .8rem; color: #166534; background: #dcfce7; font-weight: 800; }
@media (max-width: 650px) { .time-grid, .mode-row { flex-direction: column; }.finished { align-items: flex-start; flex-direction: column; gap: .7rem; } }
</style>
