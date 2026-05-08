import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'

// Views
import HomeView from './views/HomeView.vue'
import UploadView from './views/UploadView.vue'
import DashboardView from './views/DashboardView.vue'
import JobMatchView from './views/JobMatchView.vue'
import HistoryView from './views/HistoryView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { title: 'Overview' } },
    { path: '/upload', name: 'upload', component: UploadView, meta: { title: 'Upload Resume' } },
    { path: '/analysis/:id', name: 'analysis', component: DashboardView, props: true, meta: { title: 'Analysis' } },
    { path: '/job-match/:id', name: 'job-match', component: JobMatchView, props: true, meta: { title: 'Job Match' } },
    { path: '/history', name: 'history', component: HistoryView, meta: { title: 'History' } },
  ]
})

router.afterEach((to) => {
  const pageTitle = to.meta?.title ? `${to.meta.title} | CVInsight` : 'CVInsight'
  document.title = pageTitle
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
