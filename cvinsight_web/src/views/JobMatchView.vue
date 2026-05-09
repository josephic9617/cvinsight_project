<script setup>
import { ref, onMounted } from 'vue'
import { Target, Loader2, CheckCircle2, XCircle, AlertCircle, Sparkles, ArrowLeft } from 'lucide-vue-next'
import api, { getErrorMessage } from '../lib/api'

const props = defineProps(['id'])
const analysis = ref(null)
const jobDescription = ref('')
const isMatching = ref(false)
const matchResult = ref(null)
const error = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get(`/analysis/${props.id}`)
    analysis.value = res.data
    // If already matched, show results
    if (analysis.value.job_match_score !== null) {
      matchResult.value = analysis.value
      jobDescription.value = analysis.value.job_description
    }
  } catch (err) {
    error.value = getErrorMessage(err, 'Unable to load this analysis.')
  } finally {
    loading.value = false
  }
})

const runJobMatch = async () => {
  if (!jobDescription.value.trim()) return
  
  isMatching.value = true
  error.value = null
  
  try {
    const res = await api.post('/job-match', {
      analysis_id: parseInt(props.id),
      job_description: jobDescription.value
    })
    matchResult.value = res.data
  } catch (err) {
    error.value = getErrorMessage(err, 'Failed to run job match. Please try again.')
  } finally {
    isMatching.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-10 pb-20">
    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-12 h-12 border-4 border-accent-primary/20 border-t-accent-primary rounded-full animate-spin"></div>
    </div>

    <div v-else>
    <template v-if="analysis">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <RouterLink :to="`/analysis/${props.id}`" class="text-sm text-gray-500 hover:text-white flex items-center gap-1 mb-2">
          <ArrowLeft class="w-4 h-4" /> Back to analysis
        </RouterLink>
        <h1 class="text-4xl font-bold font-outfit text-white">Job Match Mode</h1>
        <p class="text-gray-400 mt-2">Compare your resume against a specific job description.</p>
      </div>
      <div v-if="analysis" class="text-right hidden md:block">
        <p class="text-xs font-bold text-gray-500 uppercase">Selected Resume</p>
        <p class="text-sm font-bold text-white">{{ analysis.filename }}</p>
      </div>
    </div>
    </template>

    <div v-else class="glass p-8 rounded-3xl">
      <h2 class="text-2xl font-bold font-outfit text-white mb-2">Analysis not found</h2>
      <p class="text-sm text-gray-400">Open an existing analysis before running job matching.</p>
    </div>

    <div v-if="error" class="p-4 rounded-2xl bg-accent-danger/10 border border-accent-danger/20 flex items-start gap-3 text-accent-danger">
      <AlertCircle class="w-5 h-5 mt-0.5 shrink-0" />
      <p class="text-sm font-medium">{{ error }}</p>
    </div>

    <!-- Input Section -->
    <div v-if="analysis" class="glass p-8 rounded-3xl space-y-6">
      <div class="flex items-center gap-2 text-accent-primary">
        <Target class="w-5 h-5" />
        <h3 class="font-bold font-outfit">Paste Job Description</h3>
      </div>
      <textarea 
        v-model="jobDescription"
        class="w-full h-64 bg-dark-700/50 border border-dark-600 rounded-2xl p-6 text-gray-200 focus:outline-none focus:border-accent-primary transition-all resize-none placeholder:text-gray-600"
        placeholder="Paste the full job description here (responsibilities, requirements, skills...)"
      ></textarea>
      <div class="flex justify-end">
        <button 
          @click="runJobMatch"
          :disabled="!jobDescription.trim() || isMatching"
          class="px-8 py-3 bg-accent-primary text-white font-bold rounded-xl hover:bg-indigo-500 transition-all disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-accent-primary/20"
        >
          <Loader2 v-if="isMatching" class="w-5 h-5 animate-spin" />
          <Sparkles v-else class="w-5 h-5" />
          {{ isMatching ? 'AI is comparing...' : 'Analyze Match' }}
        </button>
      </div>
    </div>

    <!-- Results Section -->
    <div v-if="matchResult" class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div class="glass p-10 rounded-3xl relative overflow-hidden">
        <div class="absolute top-0 right-0 p-8">
          <div class="w-32 h-32 rounded-full border-8 border-dark-700 flex items-center justify-center relative">
            <div 
              class="absolute inset-0 border-8 rounded-full border-t-accent-primary border-r-accent-primary transition-all duration-1000"
              :style="{ transform: `rotate(${matchResult.job_match_score * 3.6}deg)` }"
            ></div>
            <div class="text-center">
              <span class="text-3xl font-black font-outfit text-white">{{ matchResult.job_match_score }}%</span>
              <p class="text-[10px] font-bold text-gray-500 uppercase">Match</p>
            </div>
          </div>
        </div>

        <div class="relative z-10 max-w-xl">
          <h2 class="text-3xl font-bold font-outfit text-white mb-4">Comparison Results</h2>
          <p class="text-gray-400 leading-relaxed mb-6">
            Based on the job description provided, your resume has a <span class="text-accent-primary font-bold">{{ matchResult.job_match_score }}%</span> matching rate. 
            Here's what the AI found:
          </p>
        </div>

        <div class="grid md:grid-cols-2 gap-8 mt-10">
          <div class="space-y-4">
            <h4 class="text-sm font-bold text-accent-success flex items-center gap-2">
              <CheckCircle2 class="w-4 h-4" /> Matched Skills
            </h4>
            <div class="flex flex-wrap gap-2">
              <span v-for="skill in matchResult.job_matched_skills" :key="skill" class="px-3 py-1.5 bg-accent-success/10 text-accent-success text-xs font-bold rounded-xl border border-accent-success/20 flex items-center gap-2 group hover:bg-accent-success/20 transition-all">
                <span class="w-1 h-1 rounded-full bg-accent-success group-hover:scale-150 transition-transform"></span>
                {{ skill }}
              </span>
              <p v-if="!matchResult.job_matched_skills.length" class="text-xs text-gray-500 italic">No significant matches found.</p>
            </div>
          </div>

          <div class="space-y-4">
            <h4 class="text-sm font-bold text-accent-danger flex items-center gap-2">
              <XCircle class="w-4 h-4" /> Missing Skills
            </h4>
            <div class="flex flex-wrap gap-2">
              <span v-for="skill in matchResult.job_missing_skills" :key="skill" class="px-3 py-1.5 bg-accent-danger/10 text-accent-danger text-xs font-bold rounded-xl border border-accent-danger/20 flex items-center gap-2 group hover:bg-accent-danger/20 transition-all">
                <span class="w-1 h-1 rounded-full bg-accent-danger group-hover:scale-150 transition-transform"></span>
                {{ skill }}
              </span>
              <p v-if="!matchResult.job_missing_skills.length" class="text-xs text-gray-500 italic">No major missing skills detected.</p>
            </div>
          </div>
        </div>

        <!-- Skill Gap Analysis -->
        <div class="mt-12 pt-8 border-t border-dark-700">
          <h4 class="text-xs font-bold text-gray-500 uppercase tracking-widest mb-6">Skill Alignment Visualization</h4>
          <div class="space-y-4">
            <div class="flex items-center gap-4">
              <div class="flex-1 bg-dark-700 h-3 rounded-full overflow-hidden flex">
                <div 
                  class="h-full bg-accent-success transition-all duration-1000 delay-300"
                  :style="{ width: `${(matchResult.job_matched_skills.length / (matchResult.job_matched_skills.length + matchResult.job_missing_skills.length || 1)) * 100}%` }"
                ></div>
                <div 
                  class="h-full bg-accent-danger/30 transition-all duration-1000 delay-500"
                  :style="{ width: `${(matchResult.job_missing_skills.length / (matchResult.job_matched_skills.length + matchResult.job_missing_skills.length || 1)) * 100}%` }"
                ></div>
              </div>
              <span class="text-xs font-bold text-white whitespace-nowrap">
                {{ matchResult.job_matched_skills.length }} / {{ matchResult.job_matched_skills.length + matchResult.job_missing_skills.length }} Skills
              </span>
            </div>
            <div class="flex justify-between text-[10px] font-bold text-gray-500 uppercase">
              <span class="text-accent-success">Matched</span>
              <span class="text-accent-danger">Missing</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Advice Card -->
      <div class="glass p-8 rounded-3xl bg-accent-primary/5 border-accent-primary/20 border flex gap-6 items-start">
        <div class="w-12 h-12 bg-accent-primary/20 rounded-2xl flex items-center justify-center text-accent-primary shrink-0">
          <AlertCircle class="w-6 h-6" />
        </div>
        <div>
          <h4 class="text-lg font-bold text-white font-outfit mb-2">Tailoring Advice</h4>
          <p class="text-gray-300 leading-relaxed italic text-sm">
            {{ matchResult.job_recommendation || (matchResult.job_missing_skills.length
              ? 'Use the missing skills as a checklist. Add them only where they are genuinely reflected in your work.'
              : 'Your resume already aligns well with this role.') }}
          </p>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>
