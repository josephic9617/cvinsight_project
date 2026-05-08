<script setup>
import { ref, computed, onMounted } from 'vue'
import { FileText, ChevronRight, Calendar, Search } from 'lucide-vue-next'
import api, { getErrorMessage } from '../lib/api'

const history = ref([])
const loading = ref(true)
const error = ref(null)
const search = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/history')
    history.value = res.data
  } catch (err) {
    error.value = getErrorMessage(err, 'Unable to load analysis history.')
  } finally {
    loading.value = false
  }
})

const getScoreColor = (score) => {
  if (!score) return 'text-gray-500'
  if (score >= 80) return 'text-accent-success'
  if (score >= 60) return 'text-accent-warning'
  return 'text-accent-danger'
}

const filteredHistory = computed(() => {
  const query = search.value.trim().toLowerCase()
  if (!query) return history.value

  return history.value.filter((item) => item.filename.toLowerCase().includes(query))
})
</script>

<template>
  <div class="space-y-8">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
      <div>
        <h1 class="text-4xl font-bold font-outfit text-white">History</h1>
        <p class="text-gray-400 mt-2">Manage and view your past resume analyses.</p>
      </div>
      
      <div class="flex items-center gap-3">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input 
            v-model="search"
            type="text" 
            placeholder="Search resumes..." 
            class="pl-10 pr-4 py-2 bg-dark-800 border border-dark-700 rounded-xl text-sm focus:outline-none focus:border-accent-primary w-64"
          />
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-12 h-12 border-4 border-accent-primary/20 border-t-accent-primary rounded-full animate-spin"></div>
    </div>

    <div v-else-if="error" class="glass p-10 rounded-3xl border border-accent-danger/20">
      <h3 class="text-xl font-bold text-white mb-2">History unavailable</h3>
      <p class="text-gray-400">{{ error }}</p>
    </div>

    <div v-else-if="history.length === 0" class="glass p-20 rounded-3xl text-center">
      <div class="w-20 h-20 bg-dark-700 rounded-full flex items-center justify-center mx-auto mb-6 text-gray-500">
        <FileText class="w-10 h-10" />
      </div>
      <h3 class="text-xl font-bold text-white mb-2">No analyses found</h3>
      <p class="text-gray-400 mb-8">Start by uploading your first resume for analysis.</p>
      <RouterLink to="/upload" class="px-8 py-3 bg-accent-primary text-white font-bold rounded-xl hover:bg-indigo-500 transition-all">
        Upload Now
      </RouterLink>
    </div>

    <div v-else-if="filteredHistory.length === 0" class="glass p-10 rounded-3xl text-center">
      <h3 class="text-xl font-bold text-white mb-2">No matching resumes</h3>
      <p class="text-gray-400">Try a different filename or clear the current search.</p>
    </div>

    <div v-else class="grid gap-4">
      <div 
        v-for="item in filteredHistory" 
        :key="item.id"
        class="glass p-6 rounded-2xl flex items-center justify-between group hover:border-accent-primary/30 transition-all cursor-pointer"
        @click="$router.push(`/analysis/${item.id}`)"
      >
        <div class="flex items-center gap-5">
          <div class="w-14 h-14 bg-accent-primary/10 rounded-2xl flex items-center justify-center text-accent-primary group-hover:scale-110 transition-transform">
            <FileText class="w-7 h-7" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-white group-hover:text-accent-primary transition-colors">{{ item.filename }}</h3>
            <div class="flex items-center gap-4 mt-1">
              <span class="flex items-center gap-1.5 text-xs text-gray-500">
                <Calendar class="w-3.5 h-3.5" />
                {{ new Date(item.created_at).toLocaleDateString() }}
              </span>
              <span class="text-xs font-bold" :class="getScoreColor(item.overall_score)">
                Score: {{ item.overall_score || 'N/A' }}
              </span>
              <span v-if="item.job_match_score" class="text-xs font-bold text-accent-secondary">
                Match: {{ item.job_match_score }}%
              </span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <div class="p-2 bg-dark-700 rounded-xl text-gray-400 group-hover:bg-accent-primary group-hover:text-white transition-all">
            <ChevronRight class="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
