<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Upload, FileText, Loader2, AlertCircle, CheckCircle2 } from 'lucide-vue-next'
import api, { getErrorMessage } from '../lib/api'

const router = useRouter()
const isDragging = ref(false)
const isUploading = ref(false)
const file = ref(null)
const error = ref(null)

const allowedExtensions = ['pdf', 'doc', 'docx']
const maxFileSizeBytes = 10 * 1024 * 1024

const handleFileChange = (e) => {
  const selectedFile = e.target.files[0]
  if (selectedFile) validateAndSetFile(selectedFile)
}

const handleDrop = (e) => {
  isDragging.value = false
  const droppedFile = e.dataTransfer.files[0]
  if (droppedFile) validateAndSetFile(droppedFile)
}

const validateAndSetFile = (f) => {
  error.value = null

  const extension = f.name.split('.').pop()?.toLowerCase()
  if (!extension || !allowedExtensions.includes(extension)) {
    error.value = 'Please upload a PDF, DOC, or DOCX file.'
    return
  }

  if (f.size > maxFileSizeBytes) {
    error.value = 'File size must be 10MB or less.'
    return
  }

  file.value = f
}

const uploadResume = async () => {
  if (!file.value) return
  
  isUploading.value = true
  error.value = null
  const formData = new FormData()
  formData.append('file', file.value)

  try {
    const res = await api.post('/upload', formData)
    const analysisId = res.data.analysis_id
    
    // Start analysis automatically
    await api.post('/analyze', { analysis_id: analysisId })
    
    router.push(`/analysis/${analysisId}`)
  } catch (err) {
    error.value = getErrorMessage(err, 'Upload failed. Please try again.')
    isUploading.value = false
  }
}

const formatFileSize = (size) => {
  if (size < 1024 * 1024) {
    return `${Math.round(size / 1024)} KB`
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}
</script>

<template>
  <div class="max-w-3xl mx-auto py-10">
    <div class="text-center mb-12">
      <h1 class="text-4xl font-bold font-outfit text-white mb-4">Upload Your Resume</h1>
      <p class="text-gray-400">Get detailed AI analysis and ATS optimization in seconds.</p>
    </div>

    <div 
      class="relative group"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div 
        class="border-2 border-dashed rounded-3xl p-16 transition-all duration-300 flex flex-col items-center justify-center gap-6"
        :class="[
          isDragging ? 'border-accent-primary bg-accent-primary/5 scale-[1.02]' : 'border-dark-700 hover:border-dark-600 bg-dark-800/30',
          file ? 'border-accent-success/50 bg-accent-success/5' : ''
        ]"
      >
        <div 
          class="w-20 h-20 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110"
          :class="file ? 'bg-accent-success/20 text-accent-success' : 'bg-dark-700 text-gray-400'"
        >
          <FileText v-if="file" class="w-10 h-10" />
          <Upload v-else class="w-10 h-10" />
        </div>

        <div v-if="!file" class="text-center">
          <p class="text-lg font-semibold text-white mb-1">Drag and drop your file</p>
          <p class="text-sm text-gray-500">Supports PDF, DOC, and DOCX up to 10MB</p>
          <input 
            type="file" 
            class="hidden" 
            id="fileInput" 
            accept=".pdf,.doc,.docx" 
            @change="handleFileChange"
          />
          <label 
            for="fileInput" 
            class="mt-6 inline-block px-6 py-2 bg-dark-700 text-white text-sm font-bold rounded-xl cursor-pointer hover:bg-dark-600 transition-colors"
          >
            Browse Files
          </label>
        </div>

        <div v-else class="text-center">
          <p class="text-lg font-bold text-white mb-1">{{ file.name }}</p>
          <p class="text-xs text-gray-500 mb-2">{{ formatFileSize(file.size) }}</p>
          <p class="text-sm text-accent-success flex items-center justify-center gap-1">
            <CheckCircle2 class="w-4 h-4" /> Ready for analysis
          </p>
          <button 
            @click="file = null" 
            class="mt-4 text-xs text-gray-500 hover:text-gray-300 underline"
            :disabled="isUploading"
          >
            Choose another file
          </button>
        </div>
      </div>

      <!-- Loading Overlay -->
      <div v-if="isUploading" class="absolute inset-0 bg-dark-900/80 backdrop-blur-sm rounded-3xl flex flex-col items-center justify-center z-10">
        <Loader2 class="w-12 h-12 text-accent-primary animate-spin mb-4" />
        <p class="text-xl font-bold text-white font-outfit">AI is analyzing your resume...</p>
        <p class="text-sm text-gray-400 mt-2">This may take up to 30 seconds</p>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-6 p-4 rounded-2xl bg-accent-danger/10 border border-accent-danger/20 flex items-start gap-3 text-accent-danger">
      <AlertCircle class="w-5 h-5 mt-0.5 shrink-0" />
      <p class="text-sm font-medium">{{ error }}</p>
    </div>

    <div class="mt-10 flex justify-center">
      <button 
        @click="uploadResume"
        :disabled="!file || isUploading"
        class="px-10 py-4 bg-accent-primary text-white font-bold rounded-2xl shadow-xl shadow-accent-primary/20 hover:bg-indigo-500 transition-all disabled:opacity-50 disabled:hover:bg-accent-primary flex items-center gap-2"
      >
        Start AI Analysis
      </button>
    </div>
  </div>
</template>
