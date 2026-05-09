<script setup>
import { ref, onMounted } from 'vue'
import { 
  FileText, Loader2, Sparkles, ArrowLeft, 
  Copy, CheckCircle2, AlertCircle, Wand2 
} from 'lucide-vue-next'
import api, { getErrorMessage } from '../lib/api'

const props = defineProps(['id'])
const analysis = ref(null)
const jobDescription = ref('')
const selectedTone = ref('professional')
const isGenerating = ref(false)
const coverLetter = ref('')
const error = ref(null)
const loading = ref(true)
const copied = ref(false)

const loadingTexts = [
  'Analyzing job description...', 
  'Matching your skills...', 
  'Crafting professional intro...', 
  'Refining cover letter...', 
  'Adding finishing touches...'
]
const currentLoadingText = ref('Writing with AI...')
let loadingInterval = null

const tones = [
  { id: 'professional', label: 'Professional', icon: '👔' },
  { id: 'creative', label: 'Creative', icon: '🎨' },
  { id: 'concise', label: 'Concise', icon: '⚡' }
]

onMounted(async () => {
  try {
    const res = await api.get(`/analysis/${props.id}`)
    analysis.value = res.data
    if (analysis.value.cover_letter) {
      coverLetter.value = analysis.value.cover_letter
      jobDescription.value = analysis.value.cover_letter_jd || analysis.value.job_description || ''
    } else {
      jobDescription.value = analysis.value.job_description || ''
    }
  } catch (err) {
    error.value = getErrorMessage(err, 'Unable to load analysis.')
  } finally {
    loading.value = false
  }
})

const generateLetter = async () => {
  if (!jobDescription.value.trim()) {
    error.value = 'Please provide a job description first.'
    return
  }

  isGenerating.value = true
  error.value = null
  
  let textIndex = 0
  currentLoadingText.value = loadingTexts[0]
  loadingInterval = setInterval(() => {
    textIndex = (textIndex + 1) % loadingTexts.length
    currentLoadingText.value = loadingTexts[textIndex]
  }, 2500)

  try {
    const res = await api.post('/generate-cover-letter', {
      analysis_id: parseInt(props.id),
      job_description: jobDescription.value,
      tone: selectedTone.value
    })
    coverLetter.value = res.data.cover_letter
  } catch (err) {
    error.value = getErrorMessage(err, 'Failed to generate cover letter.')
  } finally {
    isGenerating.value = false
    clearInterval(loadingInterval)
  }
}

const copyToClipboard = async () => {
  if (!coverLetter.value) return
  try {
    await navigator.clipboard.writeText(coverLetter.value)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  } catch (err) {
    error.value = 'Failed to copy to clipboard.'
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-10 pb-20">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <RouterLink :to="`/analysis/${props.id}`" class="text-sm text-gray-500 hover:text-white flex items-center gap-1 mb-2">
          <ArrowLeft class="w-4 h-4" /> Back to analysis
        </RouterLink>
        <h1 class="text-4xl font-bold font-outfit text-white">Cover Letter AI</h1>
        <p class="text-gray-400 mt-2">Generate a tailored cover letter in seconds.</p>
      </div>
      <div v-if="analysis" class="text-right hidden md:block">
        <p class="text-xs font-bold text-gray-500 uppercase">Targeting Resume</p>
        <p class="text-sm font-bold text-white">{{ analysis.filename }}</p>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-12 h-12 border-4 border-accent-primary/20 border-t-accent-primary rounded-full animate-spin"></div>
    </div>

    <div v-else class="grid lg:grid-cols-5 gap-10">
      <!-- Controls Column -->
      <div class="lg:col-span-2 space-y-8">
        <div class="glass p-6 rounded-3xl space-y-6">
          <div class="space-y-4">
            <label class="text-xs font-bold text-gray-500 uppercase tracking-wider block">1. Choose Tone</label>
            <div class="grid grid-cols-3 gap-3">
              <button 
                v-for="tone in tones" 
                :key="tone.id"
                @click="selectedTone = tone.id"
                class="flex flex-col items-center justify-center p-4 rounded-2xl border transition-all"
                :class="selectedTone === tone.id 
                  ? 'bg-accent-primary/10 border-accent-primary text-white' 
                  : 'bg-dark-700/30 border-dark-600 text-gray-400 hover:border-gray-500'"
              >
                <span class="text-xl mb-1">{{ tone.icon }}</span>
                <span class="text-[10px] font-bold uppercase">{{ tone.label }}</span>
              </button>
            </div>
          </div>

          <div class="space-y-4">
            <label class="text-xs font-bold text-gray-500 uppercase tracking-wider block">2. Job Description</label>
            <textarea 
              v-model="jobDescription"
              class="w-full h-48 bg-dark-700/50 border border-dark-600 rounded-2xl p-4 text-sm text-gray-200 focus:outline-none focus:border-accent-primary transition-all resize-none placeholder:text-gray-600"
              placeholder="Paste the job description here..."
            ></textarea>
          </div>

          <button 
            @click="generateLetter"
            :disabled="!jobDescription.trim() || isGenerating"
            class="w-full py-4 bg-accent-primary text-white font-bold rounded-2xl hover:bg-indigo-500 transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-xl shadow-accent-primary/20"
          >
            <Loader2 v-if="isGenerating" class="w-5 h-5 animate-spin" />
            <Sparkles v-else class="w-5 h-5" />
            {{ isGenerating ? currentLoadingText : 'Generate Cover Letter' }}
          </button>
        </div>

        <div v-if="error" class="p-4 rounded-2xl bg-accent-danger/10 border border-accent-danger/20 flex items-start gap-3 text-accent-danger">
          <AlertCircle class="w-5 h-5 mt-0.5 shrink-0" />
          <p class="text-sm font-medium">{{ error }}</p>
        </div>
      </div>

      <!-- Content Column -->
      <div class="lg:col-span-3">
        <div class="glass min-h-[600px] rounded-3xl overflow-hidden flex flex-col relative">
          <!-- Letter Toolbar -->
          <div class="p-6 border-b border-dark-700 flex items-center justify-between bg-dark-800/50">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-accent-primary/10 rounded-xl flex items-center justify-center text-accent-primary">
                <FileText class="w-5 h-5" />
              </div>
              <h3 class="font-bold text-white font-outfit">Resulting Letter</h3>
            </div>
            <button 
              v-if="coverLetter"
              @click="copyToClipboard"
              class="flex items-center gap-2 px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white text-sm font-bold rounded-xl transition-all"
            >
              <CheckCircle2 v-if="copied" class="w-4 h-4 text-accent-success" />
              <Copy v-else class="w-4 h-4" />
              {{ copied ? 'Copied!' : 'Copy Text' }}
            </button>
          </div>

          <!-- Letter Body -->
          <div class="flex-1 p-10 overflow-y-auto font-serif leading-relaxed text-gray-300">
            <div v-if="!coverLetter && !isGenerating" class="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-50">
              <Wand2 class="w-16 h-16 text-gray-600" />
              <div>
                <p class="text-xl font-bold font-outfit text-white">Ready to create</p>
                <p class="text-sm">Click generate to see the AI magic.</p>
              </div>
            </div>

            <div v-else-if="isGenerating" class="space-y-4 animate-pulse">
              <div class="h-4 bg-dark-700 rounded w-1/4"></div>
              <div class="h-4 bg-dark-700 rounded w-1/3 mt-8"></div>
              <div class="h-4 bg-dark-700 rounded w-full"></div>
              <div class="h-4 bg-dark-700 rounded w-full"></div>
              <div class="h-4 bg-dark-700 rounded w-5/6"></div>
              <div class="h-4 bg-dark-700 rounded w-full mt-6"></div>
              <div class="h-4 bg-dark-700 rounded w-full"></div>
              <div class="h-4 bg-dark-700 rounded w-4/5"></div>
            </div>

            <div v-else class="whitespace-pre-wrap text-lg animate-in fade-in duration-700">
              {{ coverLetter }}
            </div>
          </div>

          <!-- Bottom Glass Effect -->
          <div class="absolute bottom-0 inset-x-0 h-20 bg-gradient-to-t from-dark-900 to-transparent pointer-events-none"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-serif {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
</style>
