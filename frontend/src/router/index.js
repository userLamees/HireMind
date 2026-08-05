import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import InterviewView from '../views/InterviewView.vue'
import ResultsView from '../views/ResultsView.vue'
import { hasResult } from '../stores/session'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/interview', name: 'interview', component: InterviewView },
  {
    path: '/results',
    name: 'results',
    component: ResultsView,
    // Landing here directly (refresh, pasted URL) means there is nothing to
    // show, so send the user back to the start instead of an empty page.
    beforeEnter: () => (hasResult() ? true : { name: 'home' }),
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
