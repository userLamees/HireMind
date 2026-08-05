import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import InterviewView from '../views/InterviewView.vue'
import ResultsView from '../views/ResultsView.vue'
import SummaryView from '../views/SummaryView.vue'
import { hasResult } from '../stores/session'

// Landing on a results page directly (refresh, pasted URL) means there is
// nothing to show, so send the user back to the start instead of an empty page.
const requireResult = () => (hasResult() ? true : { name: 'home' })

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/interview', name: 'interview', component: InterviewView },
  { path: '/results', name: 'results', component: ResultsView, beforeEnter: requireResult },
  { path: '/summary', name: 'summary', component: SummaryView, beforeEnter: requireResult },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
