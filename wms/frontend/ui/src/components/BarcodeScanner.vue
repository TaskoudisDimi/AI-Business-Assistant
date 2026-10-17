<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { IScannerControls } from '@zxing/browser'

/* Camera barcode scanner with a typed fallback. USB/Bluetooth scanners act as a
   keyboard and "type" the code followed by Enter, so the input field handles them too. */
const props = withDefaults(defineProps<{ continuous?: boolean }>(), { continuous: false })
const emit = defineEmits<{ (e: 'detected', code: string): void }>()

const { t } = useI18n()
const video = ref<HTMLVideoElement | null>(null)
const manual = ref('')
const cameraOn = ref(false)
const cameraError = ref('')
const lastCode = ref('')
let controls: IScannerControls | null = null
let lastAt = 0

function report(code: string) {
  const now = Date.now()
  // The camera reads the same code many times per second; ignore repeats for 1.5 s
  if (code === lastCode.value && now - lastAt < 1500) return
  lastCode.value = code
  lastAt = now
  navigator.vibrate?.(40)
  emit('detected', code)
  if (!props.continuous) stopCamera()
}

async function startCamera() {
  cameraError.value = ''
  if (!navigator.mediaDevices?.getUserMedia) {
    cameraError.value = t('scanner.noCamera')
    return
  }
  try {
    const { BrowserMultiFormatReader } = await import('@zxing/browser')
    const reader = new BrowserMultiFormatReader()
    cameraOn.value = true
    controls = await reader.decodeFromConstraints(
      { video: { facingMode: 'environment' } },
      video.value ?? undefined,
      (result) => { if (result) report(result.getText()) },
    )
  } catch {
    cameraOn.value = false
    cameraError.value = t('scanner.denied')
  }
}

function stopCamera() {
  controls?.stop()
  controls = null
  cameraOn.value = false
}

function submitManual() {
  const code = manual.value.trim()
  if (!code) return
  emit('detected', code)
  manual.value = ''
}

onMounted(() => { if (window.matchMedia('(pointer: coarse)').matches) startCamera() })
onBeforeUnmount(stopCamera)
</script>

<template>
  <div class="scanner">
    <div v-show="cameraOn" class="viewport">
      <video ref="video" muted playsinline />
      <span class="frame" />
    </div>

    <div class="row">
      <input
        v-model="manual"
        class="ui-input"
        :placeholder="t('scanner.placeholder')"
        inputmode="numeric"
        autofocus
        @keydown.enter.prevent="submitManual"
      />
      <button class="ui-btn ui-btn--ghost" type="button" @click="cameraOn ? stopCamera() : startCamera()">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M7 8v8M11 8v8M14 8v8M17 8v8"/></svg>
        {{ cameraOn ? t('scanner.stop') : t('scanner.camera') }}
      </button>
    </div>
    <p v-if="cameraError" class="ui-hint err">{{ cameraError }}</p>
    <p v-else class="ui-hint">{{ t('scanner.hint') }}</p>
  </div>
</template>

<style scoped>
.scanner { display: flex; flex-direction: column; gap: .6rem; }
.viewport { position: relative; border-radius: var(--r-lg); overflow: hidden; background: #000; aspect-ratio: 4 / 3; }
video { width: 100%; height: 100%; object-fit: cover; display: block; }
.frame {
  position: absolute; left: 12%; right: 12%; top: 30%; bottom: 30%;
  border: 2px solid rgba(255, 255, 255, .85); border-radius: 10px;
  box-shadow: 0 0 0 999px rgba(0, 0, 0, .35);
}
.row { display: flex; gap: .5rem; }
.row .ui-input { flex: 1; }
.err { color: var(--red); }
</style>
