<template>
  <div class="login-wrapper">
    <div class="login-container">
      <el-card class="login-card" :body-style="{ padding: '40px' }">
        <div class="login-header">
          <h2 class="title">自主學習導航系統</h2>
          <p class="subtitle">請登入您的帳號以繼續</p>
        </div>

        <el-form label-position="top" @keyup.enter="login">
          <el-form-item label="帳號">
            <el-input 
              v-model="username" 
              placeholder="請輸入帳號" 
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item label="密碼">
            <el-input 
              v-model="password" 
              type="password" 
              placeholder="請輸入密碼" 
              show-password 
              prefix-icon="Lock"
            />
          </el-form-item>

          <div class="button-group">
            <el-button 
              type="primary" 
              @click="login" 
              class="main-btn" 
              :loading="isLoading"
            >
              登入
            </el-button>
            
            <div class="footer">
              <span>沒有帳號嗎？</span>
              <el-button link type="primary" @click="router.push('/register')">立即註冊</el-button>
            </div>
          </div>
        </el-form>
      </el-card>

      <div class="notice-info">
        <el-alert
          title="環境公告"
          type="warning"
          description="本試用環境將於 2026.01.31 關閉並刪除所有資料。如需長期使用請參考 GitHub 原始碼。"
          show-icon
          :closable="false"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// 1. 導入統一封裝的 request
import request from '@/api/request.js' 

  
const router = useRouter()
const username = ref('')
const password = ref('')
const isLoading = ref(false)

const login = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('請填寫帳號密碼')
    return
  }

  isLoading.value = true
  try {
    // 2. 使用封裝後的 request，路徑簡化且自動讀取環境變數
    const data = await request.post('/auth/login', {
      username: username.value,
      password: password.value
    })
  
    // 因為 request.js 攔截器已經處理過 res.data，這裡直接拿到的就是後端回傳內容
    const { user_id, username: name } = data
    
    localStorage.setItem('user_id', user_id)
    localStorage.setItem('username', name)
    window.dispatchEvent(new Event('login'))

    ElMessage.success('登入成功')
    router.push('/calendar')
  } catch (err) {
    // 錯誤訊息已經在 request.js 的攔截器裡用 ElMessage 彈出了，這裡不需重複
    console.error('登入錯誤:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  padding: 20px; /* 防止手機貼邊 */
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.main-btn {
  width: 100%;
  height: 44px; /* 稍微加高，方便手機點擊 */
  margin-top: 10px;
  font-size: 16px;
}

.footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
}

.notice-info {
  margin-top: 20px;
}

/* 📱 手機相容界面優化 */
@media (max-width: 480px) {
  .login-wrapper {
    background-color: #ffffff; /* 手機版背景轉白 */
    align-items: flex-start; /* 從頂部開始，防止鍵盤彈出遮擋 */
    padding-top: 60px;
  }
  
  .login-card {
    border: none;
    box-shadow: none; /* 手機版移除卡片感，更像原生 App */
  }

  .title {
    font-size: 22px;
  }
  
  /* 增加表單間距，方便手指操作 */
  :deep(.el-form-item) {
    margin-bottom: 25px;
  }
}

</style>


