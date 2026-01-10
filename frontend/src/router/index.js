// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import TaskPage from '../views/TaskPage.vue'
import ProgressPage from '../views/ProgressPage.vue'
import CalendarPage from '../views/CalendarPage.vue'
import ReportPage from '../views/ReportPage.vue'
import ScorePage from '../views/ScorePage.vue'
import LoginPage from '../views/LoginPage.vue' 
import RegisterPage from '../views/RegisterPage.vue' // 1. 匯入註冊頁面
import ReviewDashboardPage from '../views/ReviewDashboard.vue'
import TeacherAnalysisPage from '../views/TeacherAnalysis.vue'
import SettingsPage from '../views/SettingsPage.vue'

const routes = [
  { path: '/', redirect: '/login' },           
  { path: '/login', component: LoginPage },    
  { path: '/register', component: RegisterPage }, // 2. 新增註冊路由
  { path: '/tasks', component: TaskPage },
  { path: '/progress', component: ProgressPage },
  { path: '/calendar', component: CalendarPage },
  { path: '/report', component: ReportPage },
  { path: '/score', component: ScorePage },
  { path: '/review', component: ReviewDashboardPage },
  { path: '/teacher', component: TeacherAnalysisPage },
  { path: '/settings', component: SettingsPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('user_id')
  
  // 定義「不需要登入」就能訪問的白名單
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)

  // 1. 如果已經登入，卻還想去登入或註冊頁面
  if (publicPages.includes(to.path) && isAuthenticated) {
    next('/calendar') 
  } 
  // 2. 如果沒登入，且想去需要權限的頁面
  else if (authRequired && !isAuthenticated) {
    next('/login')
  } 
  // 3. 其他情況
  else {
    next()
  }
})