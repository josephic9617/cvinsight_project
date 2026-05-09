<script setup>
import { ref, onMounted } from 'vue'
import { 
  TrendingUp, AlertTriangle, Lightbulb, Search, 
  ArrowLeft, Target, Sparkles, MessageSquare, CheckCircle2,
  FileText
} from 'lucide-vue-next'
import api, { getErrorMessage } from '../lib/api'

const props = defineProps(['id'])
const analysis = ref(null)
const loading = ref(true)
const loadError = ref(null)
const notice = ref(null)
const summaryCopied = ref(false)

onMounted(async () => {
  try {
    const res = await api.get(`/analysis/${props.id}`)
    analysis.value = res.data
  } catch (err) {
    loadError.value = getErrorMessage(err, 'Unable to load this analysis.')
  } finally {
    loading.value = false
  }
})

const getScoreColor = (score) => {
  if (score == null) return 'text-gray-500'
  if (score >= 80) return 'text-accent-success'
  if (score >= 60) return 'text-accent-warning'
  return 'text-accent-danger'
}

const copySummary = async () => {
  if (!analysis.value?.rewritten_summary) return

  try {
    await navigator.clipboard.writeText(analysis.value.rewritten_summary)
    summaryCopied.value = true
    notice.value = null
    window.setTimeout(() => {
      summaryCopied.value = false
    }, 2000)
  } catch (err) {
    notice.value = 'Unable to copy the summary from this browser session.'
  }
}
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
    <div class="relative w-24 h-24">
      <div class="absolute inset-0 border-4 border-accent-primary/20 rounded-full"></div>
      <div class="absolute inset-0 border-4 border-accent-primary border-t-transparent rounded-full animate-spin"></div>
    </div>
  </div>

  <div v-else-if="loadError" class="glass max-w-2xl mx-auto p-8 rounded-3xl border border-accent-danger/20">
    <h1 class="text-2xl font-bold font-outfit text-white mb-2">Analysis unavailable</h1>
    <p class="text-sm text-gray-400 mb-6">{{ loadError }}</p>
    <RouterLink to="/history" class="inline-flex items-center gap-2 px-5 py-3 bg-dark-700 text-white font-bold rounded-xl hover:bg-dark-600 transition-all">
      <ArrowLeft class="w-4 h-4" /> Return to history
    </RouterLink>
  </div>

  <div v-else-if="analysis" class="space-y-8 pb-20">
    <div v-if="notice" class="p-4 rounded-2xl bg-accent-danger/10 border border-accent-danger/20 text-sm font-medium text-accent-danger">
      {{ notice }}
    </div>

    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <RouterLink to="/history" class="text-sm text-gray-500 hover:text-white flex items-center gap-1 mb-2">
          <ArrowLeft class="w-4 h-4" /> Back to history
        </RouterLink>
        <h1 class="text-3xl font-bold font-outfit text-white">{{ analysis.filename }}</h1>
        <p class="text-gray-400 text-sm mt-1">Analyzed on {{ new Date(analysis.created_at).toLocaleDateString() }}</p>
      </div>
      <div class="flex items-center gap-3">
        <RouterLink 
          :to="`/cover-letter/${analysis.id}`"
          class="px-5 py-2.5 bg-dark-700 text-white font-bold rounded-xl hover:bg-dark-600 transition-all flex items-center gap-2 border border-dark-600"
        >
          <FileText class="w-4 h-4" /> Cover Letter AI
        </RouterLink>
        <RouterLink 
          :to="`/job-match/${analysis.id}`"
          class="px-5 py-2.5 bg-accent-primary text-white font-bold rounded-xl hover:bg-indigo-500 transition-all flex items-center gap-2 shadow-lg shadow-accent-primary/20"
        >
          <Target class="w-4 h-4" /> Job Match Mode
        </RouterLink>
      </div>
    </div>

    <!-- Scores Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="glass p-6 rounded-3xl relative overflow-hidden">
        <div class="relative z-10">
          <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Resume Score</p>
          <div class="flex items-baseline gap-2">
            <span v-if="analysis.overall_score == null" class="text-4xl font-black font-outfit text-gray-500">N/A</span>
            <span v-else class="text-4xl font-black font-outfit" :class="getScoreColor(analysis.overall_score)">{{ analysis.overall_score }}</span>
            <span class="text-gray-500 font-bold">/100</span>
          </div>
          <div class="mt-4 w-full bg-dark-700 h-1.5 rounded-full overflow-hidden">
            <div 
              class="h-full bg-accent-primary transition-all duration-1000" 
              :style="{ width: `${analysis.overall_score ?? 0}%` }"
            ></div>
          </div>
        </div>
      </div>

      <div class="glass p-6 rounded-3xl">
        <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">ATS Score</p>
        <div class="flex items-baseline gap-2">
          <span v-if="analysis.ats_score == null" class="text-4xl font-black font-outfit text-gray-500">N/A</span>
          <span v-else class="text-4xl font-black font-outfit text-accent-secondary">{{ analysis.ats_score }}</span>
          <span class="text-gray-500 font-bold">/100</span>
        </div>
        <div class="mt-4 w-full bg-dark-700 h-1.5 rounded-full overflow-hidden">
          <div 
            class="h-full bg-accent-secondary transition-all duration-1000" 
            :style="{ width: `${analysis.ats_score ?? 0}%` }"
          ></div>
        </div>
      </div>

      <div class="glass p-6 rounded-3xl">
        <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Keywords Found</p>
        <div class="text-4xl font-black font-outfit text-accent-success">{{ analysis.keywords_found.length }}</div>
        <p class="text-xs text-gray-500 mt-2 font-medium">Detected ATS terms</p>
      </div>

      <div class="glass p-6 rounded-3xl">
        <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Suggestions</p>
        <div class="text-4xl font-black font-outfit text-accent-warning">{{ analysis.suggestions.length }}</div>
        <p class="text-xs text-gray-500 mt-2 font-medium">Actionable improvements</p>
      </div>
    </div>

    <!-- Main Analysis Body -->
    <div class="grid lg:grid-cols-3 gap-8">
      <div class="lg:col-span-2 space-y-8">
        <!-- Strengths & Weaknesses -->
        <div class="grid md:grid-cols-2 gap-6">
          <div class="glass p-8 rounded-3xl border-l-4 border-accent-success/50">
            <div class="flex items-center gap-3 mb-6 text-accent-success">
              <TrendingUp class="w-6 h-6" />
              <h3 class="text-xl font-bold font-outfit text-white">Strengths</h3>
            </div>
            <ul class="space-y-4">
              <li v-for="item in analysis.strengths" :key="item" class="flex gap-3 text-sm text-gray-300">
                <span class="mt-1.5 w-1.5 h-1.5 rounded-full bg-accent-success shrink-0"></span>
                {{ item }}
              </li>
              <li v-if="!analysis.strengths.length" class="text-sm text-gray-500">No strengths were returned for this analysis.</li>
            </ul>
          </div>

          <div class="glass p-8 rounded-3xl border-l-4 border-accent-danger/50">
            <div class="flex items-center gap-3 mb-6 text-accent-danger">
              <AlertTriangle class="w-6 h-6" />
              <h3 class="text-xl font-bold font-outfit text-white">Weaknesses</h3>
            </div>
            <ul class="space-y-4">
              <li v-for="item in analysis.weaknesses" :key="item" class="flex gap-3 text-sm text-gray-300">
                <span class="mt-1.5 w-1.5 h-1.5 rounded-full bg-accent-danger shrink-0"></span>
                {{ item }}
              </li>
              <li v-if="!analysis.weaknesses.length" class="text-sm text-gray-500">No weaknesses were returned for this analysis.</li>
            </ul>
          </div>
        </div>

        <!-- AI Suggestions -->
        <div class="glass p-8 rounded-3xl bg-gradient-to-br from-dark-800 to-dark-900 border border-dark-700">
          <div class="flex items-center gap-3 mb-8">
            <Lightbulb class="w-6 h-6 text-accent-warning" />
            <h3 class="text-2xl font-bold font-outfit text-white">How to Improve</h3>
          </div>
          <div class="space-y-6">
            <div v-for="(item, idx) in analysis.suggestions" :key="idx" class="flex gap-6 p-4 rounded-2xl hover:bg-dark-700/50 transition-colors">
              <div class="w-10 h-10 bg-accent-warning/10 rounded-xl flex items-center justify-center text-accent-warning shrink-0 font-bold">
                {{ idx + 1 }}
              </div>
              <p class="text-gray-300 leading-relaxed">{{ item }}</p>
            </div>
            <p v-if="!analysis.suggestions.length" class="text-sm text-gray-500">No improvement suggestions were returned for this analysis.</p>
          </div>
        </div>

        <!-- AI Rewritten Summary -->
        <div class="glass p-8 rounded-3xl relative overflow-hidden">
          <div class="absolute top-0 right-0 p-4">
            <Sparkles class="w-8 h-8 text-accent-primary/20" />
          </div>
          <div class="flex items-center gap-3 mb-6">
            <MessageSquare class="w-6 h-6 text-accent-primary" />
            <h3 class="text-xl font-bold font-outfit text-white">Professional AI Summary</h3>
          </div>
          <div class="bg-dark-700/30 p-6 rounded-2xl italic text-gray-300 leading-loose border-l-2 border-accent-primary">
            {{ analysis.rewritten_summary ? `"${analysis.rewritten_summary}"` : 'A rewritten summary is not available for this analysis.' }}
          </div>
          <button v-if="analysis.rewritten_summary" @click="copySummary" class="mt-6 inline-flex items-center gap-2 text-sm font-bold text-accent-primary hover:underline">
            <CheckCircle2 v-if="summaryCopied" class="w-4 h-4" />
            {{ summaryCopied ? 'Copied' : 'Copy to clipboard' }}
          </button>
        </div>
      </div>

      <!-- Sidebar Info -->
      <div class="space-y-8">
        <!-- Keywords -->
        <div class="glass p-8 rounded-3xl">
          <div class="flex items-center gap-3 mb-6">
            <Search class="w-5 h-5 text-accent-success" />
            <h3 class="text-lg font-bold font-outfit text-white">ATS Keywords</h3>
          </div>
          
          <div class="mb-8">
            <p class="text-xs font-bold text-gray-500 uppercase mb-4">Detected</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="tag in analysis.keywords_found" :key="tag" class="px-3 py-1 bg-accent-success/10 text-accent-success text-xs font-bold rounded-lg border border-accent-success/20">
                {{ tag }}
              </span>
              <p v-if="!analysis.keywords_found.length" class="text-xs text-gray-500 italic">No keywords were detected.</p>
            </div>
          </div>

          <div>
            <p class="text-xs font-bold text-gray-500 uppercase mb-4">Missing (Important)</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="tag in analysis.keywords_missing" :key="tag" class="px-3 py-1 bg-accent-danger/10 text-accent-danger text-xs font-bold rounded-lg border border-accent-danger/20">
                {{ tag }}
              </span>
              <p v-if="!analysis.keywords_missing.length" class="text-xs text-gray-500 italic">No important missing keywords were identified.</p>
            </div>
          </div>
        </div>

        <!-- Interview Questions -->
        <div class="glass p-8 rounded-3xl">
          <div class="flex items-center gap-3 mb-6">
            <Sparkles class="w-5 h-5 text-accent-secondary" />
            <h3 class="text-lg font-bold font-outfit text-white">Potential Interview Questions</h3>
          </div>
          <div class="space-y-4">
            <div v-for="q in analysis.interview_questions" :key="q" class="text-sm text-gray-400 p-4 bg-dark-700/30 rounded-xl border border-dark-700 group hover:border-accent-secondary/30 transition-all cursor-default">
              {{ q }}
            </div>
            <p v-if="!analysis.interview_questions.length" class="text-sm text-gray-500">No interview questions were generated for this analysis.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="glass max-w-2xl mx-auto p-8 rounded-3xl">
    <h1 class="text-2xl font-bold font-outfit text-white mb-2">Analysis not found</h1>
    <p class="text-sm text-gray-400">The requested record could not be loaded.</p>
  </div>
</template>
