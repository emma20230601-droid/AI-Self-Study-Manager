<template>
  <el-container>
    <el-header v-if="showHeader" style="display: flex; justify-content: space-between; align-items: center">
      <el-menu :default-active="$route.path" mode="horizontal" style="min-width: 1500px; overflow-x: auto" router>
        <el-menu-item index="/calendar">📅 月曆任務清單</el-menu-item>
        <el-menu-item index="/progress">📘 學習成就軌跡看板</el-menu-item>
        <el-menu-item index="/report">🎯 進度衝刺看板</el-menu-item>
        <el-menu-item index="/score">🧪 核心五科 - 學力診斷報告</el-menu-item>
        <el-menu-item index="/review">🎯 考後診斷與複習追蹤</el-menu-item>
        <el-menu-item index="/teacher">🎯 AI 教師教學診斷看板</el-menu-item>
        <el-menu-item index="/tasks">📋 學習進度總表</el-menu-item>
        <el-menu-item index="/settings">⚙️ 學習版本與年級設定</el-menu-item>
      </el-menu>

      <div style="margin-left: auto; display: flex; align-items: center">
        <p v-if="isLoggedIn" style="margin-right: 10px; color: black">
          👋 {{ username }}，歡迎回來
        </p>
        <el-button
          v-if="isLoggedIn"
          type="danger"
          :icon="SwitchButton"
          size="small"
          @click="logout"
        >
          登出
        </el-button>
      </div>
    </el-header>

    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute() // 引入 route 以監聽路徑變化
const isLoggedIn = ref(false)
const username = ref('')

// 新增此計算屬性：判斷是否顯示 Header
// 只有在非登入/註冊頁面，且確實已登入時才顯示
const showHeader = computed(() => {
  const isAuthPage = route.path === '/login' || route.path === '/register'
  return !isAuthPage && isLoggedIn.value
})

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem('user_id')
  username.value = localStorage.getItem('username') || ''

  window.addEventListener('login', () => {
    isLoggedIn.value = true
    username.value = localStorage.getItem('username') || ''
  })
})

const logout = () => {
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  isLoggedIn.value = false
  username.value = ''
  router.push('/login')
}
</script>

<style>
/* 保持你原本可能有的樣式，並確保 body 不留白邊 */
body {
  margin: 0;
}
</style>