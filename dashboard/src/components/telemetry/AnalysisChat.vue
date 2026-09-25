<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[99999]" @keydown="keyboard">
      <button
        type="button"
        aria-label="Cerrar asistente"
        class="absolute inset-0 h-full w-full cursor-default bg-gray-950/45 backdrop-blur-[2px]"
        @click="emit('close')"
      />
      <section
        ref="dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="analysis-title"
        tabindex="-1"
        class="absolute inset-y-0 end-0 flex w-full flex-col bg-gray-25 shadow-theme-xl dark:bg-gray-950 sm:max-w-[30rem] sm:border-s sm:border-gray-200 sm:dark:border-gray-800"
      >
        <header
          class="flex shrink-0 items-center justify-between gap-3 border-b border-gray-200 bg-white px-4 py-3.5 dark:border-gray-800 dark:bg-gray-900 sm:px-5"
        >
          <div class="flex min-w-0 items-center gap-3">
            <span
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-success-50 text-success-600 dark:bg-success-500/15 dark:text-success-400"
              aria-hidden="true"
            >
              <svg
                viewBox="0 0 24 24"
                class="h-6 w-6"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  d="M12 21V10m0 4C8.5 14 6 11.8 6 8c3.8 0 6 2.2 6 6Zm0-3c0-4.4 2.6-7 7-7 0 4.4-2.6 7-7 7Z"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            <div class="min-w-0">
              <h2 id="analysis-title" class="truncate font-semibold text-gray-900 dark:text-white">
                Asistente del cultivo
              </h2>
              <p class="mt-0.5 flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                <span class="h-2 w-2 rounded-full bg-success-500" />
                Análisis local de las lecturas actuales
              </p>
            </div>
          </div>
          <button
            type="button"
            aria-label="Cerrar chat"
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-gray-500 transition hover:bg-gray-100 hover:text-gray-800 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
            @click="emit('close')"
          >
            <svg
              viewBox="0 0 24 24"
              class="h-5 w-5"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="m6 6 12 12M18 6 6 18" stroke-linecap="round" />
            </svg>
          </button>
        </header>

        <div ref="scrollArea" class="min-h-0 flex-1 overflow-y-auto px-4 py-5 sm:px-5">
          <div class="mb-5 flex gap-2.5">
            <span
              class="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-success-100 text-success-700 dark:bg-success-500/20 dark:text-success-300"
              aria-hidden="true"
              >H</span
            >
            <div
              class="max-w-[88%] rounded-2xl rounded-ss-md border border-gray-200 bg-white px-4 py-3 text-sm leading-relaxed text-gray-700 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900 dark:text-gray-200"
            >
              Hola, soy el asistente de HydroGuard. Reviso los cuatro indicadores y te los explico
              en palabras simples. También podés preguntarme por uno en particular.
            </div>
          </div>

          <p
            v-if="loadingConfig"
            role="status"
            class="py-5 text-center text-sm text-gray-500 dark:text-gray-400"
          >
            Preparando el análisis…
          </p>

          <div
            role="log"
            aria-label="Conversación de análisis"
            aria-live="polite"
            class="space-y-4"
          >
            <div
              v-for="(message, index) in messages"
              :key="index"
              class="flex"
              :class="message.role === 'user' ? 'justify-end' : 'items-start gap-2.5'"
            >
              <span
                v-if="message.role === 'assistant'"
                class="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-success-100 text-xs font-semibold text-success-700 dark:bg-success-500/20 dark:text-success-300"
                aria-hidden="true"
                >H</span
              >
              <article
                class="max-w-[88%] whitespace-pre-wrap break-words rounded-2xl px-4 py-3 text-sm leading-relaxed"
                :class="
                  message.role === 'user'
                    ? 'rounded-ee-md bg-brand-500 text-white shadow-theme-xs'
                    : 'rounded-ss-md border border-gray-200 bg-white text-gray-700 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900 dark:text-gray-200'
                "
              >
                {{ message.content }}
              </article>
            </div>

            <div v-if="busy" role="status" class="flex items-start gap-2.5">
              <span
                class="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-success-100 text-xs font-semibold text-success-700 dark:bg-success-500/20 dark:text-success-300"
                aria-hidden="true"
                >H</span
              >
              <div
                class="flex items-center gap-1 rounded-2xl rounded-ss-md border border-gray-200 bg-white px-4 py-4 shadow-theme-xs dark:border-gray-800 dark:bg-gray-900"
                aria-label="Analizando"
              >
                <span
                  v-for="dot in 3"
                  :key="dot"
                  class="h-1.5 w-1.5 animate-pulse rounded-full bg-gray-400"
                />
              </div>
            </div>
          </div>

          <p
            v-if="error"
            role="alert"
            class="mt-4 rounded-xl border border-error-200 bg-error-50 p-3 text-sm text-error-700 dark:border-error-500/30 dark:bg-error-500/10 dark:text-error-300"
          >
            {{ error }}
          </p>

          <div
            v-if="config?.configured && !busy"
            class="mt-5 flex flex-wrap gap-2"
            aria-label="Preguntas sugeridas"
          >
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              type="button"
              class="rounded-full border border-gray-200 bg-white px-3 py-2 text-start text-xs font-medium text-gray-600 transition hover:border-brand-300 hover:text-brand-600 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300 dark:hover:border-brand-500/50 dark:hover:text-brand-400"
              @click="askSuggestion(suggestion)"
            >
              {{ suggestion }}
            </button>
          </div>

          <p v-if="lastMeta" class="mt-4 text-center text-xs text-gray-400 dark:text-gray-500">
            {{ lastMeta }}
          </p>
        </div>

        <footer
          class="shrink-0 border-t border-gray-200 bg-white p-3 dark:border-gray-800 dark:bg-gray-900 sm:p-4"
        >
          <form
            class="flex items-end gap-2 rounded-2xl border border-gray-300 bg-gray-25 p-2 transition focus-within:border-brand-400 focus-within:ring-2 focus-within:ring-brand-500/10 dark:border-gray-700 dark:bg-gray-950"
            @submit.prevent="send()"
          >
            <label for="analysis-question" class="sr-only">Escribí tu consulta</label>
            <textarea
              id="analysis-question"
              v-model="draft"
              rows="1"
              maxlength="1200"
              placeholder="Preguntá sobre las lecturas…"
              class="max-h-28 min-h-10 flex-1 resize-none border-0 bg-transparent px-2 py-2 text-sm text-gray-800 placeholder:text-gray-400 focus:ring-0 dark:text-gray-100"
              :disabled="busy"
              @keydown.enter.exact.prevent="send()"
            />
            <button
              type="submit"
              aria-label="Enviar mensaje"
              :disabled="busy || loadingConfig || !config?.configured || !draft.trim()"
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-500 text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:bg-gray-300 dark:disabled:bg-gray-700"
            >
              <svg
                viewBox="0 0 24 24"
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="m5 12 14-7-4 14-3-6-7-1Z" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
          </form>
          <p class="mt-2 text-center text-[11px] text-gray-400 dark:text-gray-500">
            Basado en reglas del prototipo · Sin Internet · No reemplaza una medición real
          </p>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()
interface Config {
  configured: boolean
  model: string
  csrf_token: string
}
interface Message {
  role: 'user' | 'assistant'
  content: string
}

const config = ref<Config | null>(null)
const messages = ref<Message[]>([])
const draft = ref('')
const busy = ref(false)
const loadingConfig = ref(false)
const error = ref('')
const lastMeta = ref('')
const dialog = ref<HTMLElement | null>(null)
const scrollArea = ref<HTMLElement | null>(null)
const suggestions = [
  'Actualizar resumen',
  '¿Qué debería revisar primero?',
  '¿Cómo están pH y conductividad?',
  '¿Cómo están temperatura y humedad?',
]
const initialQuestion = 'Dame un resumen claro del estado actual y qué debería revisar primero.'
let previousFocus: HTMLElement | null = null
let previousOverflow = ''
let controller: AbortController | undefined
let configRequest: Promise<void> | null = null

async function scrollToEnd() {
  await nextTick()
  scrollArea.value?.scrollTo({ top: scrollArea.value.scrollHeight, behavior: 'auto' })
}

async function loadConfig() {
  if (configRequest) return configRequest
  configRequest = (async () => {
    loadingConfig.value = true
    error.value = ''
    const abort = new AbortController()
    const timeout = setTimeout(() => abort.abort(), 5000)
    try {
      const response = await fetch('/api/v1/ai/config', { cache: 'no-store', signal: abort.signal })
      const body = await response.json()
      if (!response.ok) throw new Error(body.error || 'No se pudo iniciar el asistente.')
      config.value = body
    } catch {
      config.value = null
      error.value =
        'No se pudo conectar con el analizador local. Cerrá y volvé a abrir para reintentar.'
    } finally {
      clearTimeout(timeout)
      loadingConfig.value = false
    }
  })()
  try {
    await configRequest
  } finally {
    configRequest = null
  }
}

async function send(questionOverride?: string, showUser = true) {
  if (busy.value) return
  const question = (questionOverride ?? draft.value).trim()
  if (!question) return
  busy.value = true
  if (!config.value?.configured) await loadConfig()
  if (!config.value?.configured) {
    busy.value = false
    return
  }
  const history = messages.value
    .slice(-6)
    .map((message) => ({ role: message.role, content: message.content.slice(0, 1200) }))
  if (showUser)
    messages.value = [...messages.value, { role: 'user', content: question }].slice(
      -40,
    ) as Message[]
  draft.value = ''
  error.value = ''
  await scrollToEnd()
  controller = new AbortController()
  const timeout = setTimeout(() => controller?.abort(), 10000)
  try {
    const response = await fetch('/api/v1/ai/chat', {
      method: 'POST',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'X-Hydro-Chat-Token': config.value.csrf_token,
      },
      body: JSON.stringify({ message: question, history }),
    })
    const body = await response.json()
    if (!response.ok) throw new Error(body.error || `Error del servidor (${response.status}).`)
    if (typeof body.reply !== 'string' || !body.reply.trim())
      throw new Error('No se generó una explicación válida.')
    messages.value = [...messages.value, { role: 'assistant', content: body.reply }].slice(
      -40,
    ) as Message[]
    const captured = body.captured_at
      ? new Date(body.captured_at * 1000).toLocaleTimeString('es-AR')
      : 'sin lectura vigente'
    lastMeta.value = `Lecturas actualizadas a las ${captured}`
  } catch (caught) {
    error.value =
      caught instanceof Error && caught.name !== 'AbortError'
        ? caught.message
        : 'El analizador local no respondió. Volvé a intentarlo.'
  } finally {
    clearTimeout(timeout)
    busy.value = false
    await scrollToEnd()
  }
}

function askSuggestion(suggestion: string) {
  const question = suggestion === 'Actualizar resumen' ? initialQuestion : suggestion
  void send(question)
}

function keyboard(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('close')
    return
  }
  if (event.key !== 'Tab') return
  const items = dialog.value?.querySelectorAll<HTMLElement>(
    'button:not(:disabled), textarea:not(:disabled), a[href]',
  )
  if (!items?.length) return
  const first = items[0]!
  const last = items[items.length - 1]!
  if (
    event.shiftKey &&
    (document.activeElement === first || document.activeElement === dialog.value)
  ) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

watch(
  () => props.open,
  async (open) => {
    if (!open) {
      document.body.style.overflow = previousOverflow
      previousFocus?.focus()
      return
    }
    previousFocus = document.activeElement as HTMLElement | null
    previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    await nextTick()
    dialog.value?.focus()
    if (!config.value?.configured) await loadConfig()
  },
)

onMounted(() => void loadConfig())

onBeforeUnmount(() => {
  controller?.abort()
  if (props.open) document.body.style.overflow = previousOverflow
})
</script>
