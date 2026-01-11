<template>
  <el-container>
    <el-header v-if="showHeader" class="main-header">
      <el-menu 
        :default-active="$route.path" 
        mode="horizontal" 
        class="nav-menu" 
        router
      >
        <el-menu-item index="/calendar">📅 月曆任務清單</el-menu-item>
        <el-menu-item index="/progress">📘 學習成就軌跡看板</el-menu-item>
        <el-menu-item index="/report">🎯 進度衝刺看板</el-menu-item>
        <el-menu-item index="/score">🧪 核心五科 - 學力診斷報告</el-menu-item>
        <el-menu-item index="/review">🎯 考後診斷與複習追蹤</el-menu-item>
        <el-menu-item index="/teacher">🎯 AI 教師教學診斷看板</el-menu-item>
        <el-menu-item index="/tasks">📋 學習進度總表</el-menu-item>
        <el-menu-item index="/settings">⚙️ 學習版本與年級設定</el-menu-item>
      </el-menu>

      <div class="user-info">
        <p v-if="isLoggedIn" class="user-name">
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
/* 1. 電腦版原始設計 (不變) */
.nav-menu {
  min-width: 1500px; 
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
}

.user-info {
  margin-left: auto;
  display: flex;
  align-items: center;
  white-space: nowrap;
  padding-left: 20px;
  background: white; /* 確保滑動時遮住選單 */
  z-index: 10;
}

/* ==========================================================================
   手機版專屬 CSS (僅在 768px 以下生效)
   ========================================================================== */
@media (max-width: 768px) {
  .main-header {
    padding: 0 10px !important;
  }

  /* 覆蓋電腦版的 1500px，讓它在手機上可以橫向滑動 */
  .nav-menu {
    min-width: 0 !important; /* 解除硬編碼寬度 */
    flex: 1;
    overflow-x: auto !important; /* 開啟橫向滑動 */
    overflow-y: hidden;
    display: flex !important;
    -webkit-overflow-scrolling: touch; /* 讓滑動更順暢 */
    border-bottom: none !important;
  }

  /* 隱藏手機版的捲動條 (外觀更乾淨) */
  .nav-menu::-webkit-scrollbar {
    display: none;
  }

  :deep(.el-menu-item) {
    flex-shrink: 0 !important; /* 防止選單文字被壓扁 */
    padding: 0 15px !important;
    font-size: 14px !important;
  }

  /* 手機版縮減使用者名稱與按鈕空間，避免擠壓導覽列 */
  .user-name {
    display: none; /* 手機版通常會隱藏歡迎詞以節省空間 */
  }
  
  .user-info {
    padding-left: 10px;
  }
}
</style>
