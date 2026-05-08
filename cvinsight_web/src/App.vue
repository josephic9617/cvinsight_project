<script setup>
import { computed } from 'vue'
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { Home, Upload, History, Zap } from 'lucide-vue-next'

const route = useRoute()

const navigationItems = [
  { to: '/', label: 'Overview', icon: Home },
  { to: '/upload', label: 'Upload CV', icon: Upload },
  { to: '/history', label: 'History', icon: History },
]

const currentSection = computed(() => {
  if (route.path.startsWith('/analysis/')) return 'Analysis'
  if (route.path.startsWith('/job-match/')) return 'Job Match'
  return route.meta?.title || 'Overview'
})

const isActive = (path) => route.path === path
</script>

<template>
  <div class="flex min-h-screen bg-dark-900 font-sans text-gray-200">
    <!-- Sidebar -->
    <aside class="w-64 border-r border-dark-700 bg-dark-800/50 backdrop-blur-xl hidden lg:flex flex-col fixed h-full z-50">
      <div class="p-8">
        <div class="flex items-center gap-3">
          <div class="bg-accent-primary p-2 rounded-xl shadow-lg shadow-accent-primary/20">
            <Zap class="w-6 h-6 text-white" />
          </div>
          <span class="text-xl font-bold font-outfit tracking-tight text-white">CVInsight</span>
        </div>
      </div>

      <nav class="flex-1 px-4 space-y-2 mt-4">
        <RouterLink
          v-for="item in navigationItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
          :class="isActive(item.to) ? 'bg-accent-primary/10 text-accent-primary' : 'text-gray-400 hover:bg-dark-700 hover:text-white'"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span class="font-medium">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="p-4 mt-auto">
        <div class="glass-accent rounded-2xl p-4 relative overflow-hidden group">
          <div class="relative z-10">
            <h4 class="text-sm font-bold text-white mb-1">Sharper resume reviews</h4>
            <p class="text-xs text-gray-400 leading-relaxed">Upload a fresh version before each application to keep your score and keyword coverage current.</p>
          </div>
          <Zap class="absolute -right-4 -bottom-4 w-24 h-24 text-accent-primary/10 rotate-12 group-hover:rotate-0 transition-transform duration-500" />
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 lg:ml-64 relative">
      <!-- Navbar for mobile -->
      <header class="lg:hidden h-16 border-b border-dark-700 bg-dark-800/80 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Zap class="w-6 h-6 text-accent-primary" />
          <span class="text-lg font-bold font-outfit text-white">CVInsight</span>
        </div>
        <span class="text-sm font-medium text-gray-400">{{ currentSection }}</span>
      </header>

      <div class="p-6 pb-24 lg:p-10 lg:pb-10 max-w-7xl mx-auto">
        <RouterView v-slot="{ Component }">
          <transition 
            enter-active-class="transition duration-300 ease-out"
            enter-from-class="opacity-0 translate-y-4"
            enter-to-class="opacity-100 translate-y-0"
          >
            <component :is="Component" />
          </transition>
        </RouterView>
      </div>

      <nav class="lg:hidden fixed inset-x-0 bottom-0 z-40 border-t border-dark-700 bg-dark-800/90 backdrop-blur-xl">
        <div class="grid grid-cols-3 px-2 py-2">
          <RouterLink
            v-for="item in navigationItems"
            :key="item.to"
            :to="item.to"
            class="flex flex-col items-center gap-1 rounded-xl px-3 py-2 text-xs font-medium transition-colors"
            :class="isActive(item.to) ? 'text-accent-primary bg-accent-primary/10' : 'text-gray-400'"
          >
            <component :is="item.icon" class="w-5 h-5" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </div>
      </nav>
    </main>
  </div>
</template>

<style>
.route-enter-active,
.route-leave-active {
  transition: opacity 0.3s ease;
}

.route-enter-from,
.route-leave-to {
  opacity: 0;
}
</style>
