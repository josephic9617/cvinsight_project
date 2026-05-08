<script setup>
import { RouterLink } from 'vue-router'
import { Sparkles, Target, Zap, ShieldCheck, ArrowRight } from 'lucide-vue-next'
</script>

<template>
  <div class="space-y-12">
    <!-- Hero Section -->
    <div class="relative py-12 px-8 rounded-3xl overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-accent-primary/20 via-transparent to-accent-secondary/20"></div>
      <div class="absolute -top-24 -right-24 w-64 h-64 bg-accent-primary/10 rounded-full blur-3xl"></div>
      
      <div class="relative z-10 max-w-2xl">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-primary/10 border border-accent-primary/20 text-accent-primary text-xs font-bold mb-6">
          <Sparkles class="w-3 h-3" />
          <span>AI-POWERED RESUME ANALYSIS</span>
        </div>
        <h1 class="text-5xl lg:text-6xl font-extrabold font-outfit text-white mb-6 leading-tight">
          Supercharge Your <span class="text-transparent bg-clip-text bg-gradient-to-r from-accent-primary to-accent-secondary">Career Search.</span>
        </h1>
        <p class="text-lg text-gray-400 mb-8 leading-relaxed">
          Upload your resume and let our professional AI career assistant optimize it for ATS, 
          detect missing keywords, and match your profile with job descriptions in seconds.
        </p>
        <div class="flex flex-wrap gap-4">
          <RouterLink 
            to="/upload" 
            class="px-8 py-4 bg-accent-primary text-white font-bold rounded-2xl hover:bg-indigo-500 transition-all flex items-center gap-2 shadow-lg shadow-accent-primary/25"
          >
            Analyze Resume <ArrowRight class="w-5 h-5" />
          </RouterLink>
          <RouterLink 
            to="/history" 
            class="px-8 py-4 bg-dark-700 text-white font-bold rounded-2xl hover:bg-dark-600 transition-all"
          >
            View History
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Stats/Features -->
    <div class="grid md:grid-cols-3 gap-6">
      <div class="glass p-8 rounded-3xl group hover:border-accent-primary/30 transition-all">
        <div class="w-12 h-12 bg-accent-primary/10 rounded-2xl flex items-center justify-center mb-6 text-accent-primary group-hover:scale-110 transition-transform">
          <Zap class="w-6 h-6" />
        </div>
        <h3 class="text-xl font-bold text-white mb-2 font-outfit">Instant Insights</h3>
        <p class="text-gray-400 text-sm leading-relaxed">Get a comprehensive score and feedback on your resume's strengths and weaknesses instantly.</p>
      </div>

      <div class="glass p-8 rounded-3xl group hover:border-accent-secondary/30 transition-all">
        <div class="w-12 h-12 bg-accent-secondary/10 rounded-2xl flex items-center justify-center mb-6 text-accent-secondary group-hover:scale-110 transition-transform">
          <Target class="w-6 h-6" />
        </div>
        <h3 class="text-xl font-bold text-white mb-2 font-outfit">Job Matcher</h3>
        <p class="text-gray-400 text-sm leading-relaxed">Paste any job description to see how well you match and identify missing skills required for the role.</p>
      </div>

      <div class="glass p-8 rounded-3xl group hover:border-accent-success/30 transition-all">
        <div class="w-12 h-12 bg-accent-success/10 rounded-2xl flex items-center justify-center mb-6 text-accent-success group-hover:scale-110 transition-transform">
          <ShieldCheck class="w-6 h-6" />
        </div>
        <h3 class="text-xl font-bold text-white mb-2 font-outfit">ATS Optimizer</h3>
        <p class="text-gray-400 text-sm leading-relaxed">Ensure your resume passes automated filters with expert keyword detection and formatting advice.</p>
      </div>
    </div>
  </div>
</template>
