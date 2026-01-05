<template>
  <div 
    class="login-wrapper" 
    v-loading="isLoading"
    element-loading-text="正在登入，請稍候..."
    element-loading-background="rgba(255, 255, 255, 0.7)"
  >
    <div class="login-container">
      <el-card class="login-card" :body-style="{ padding: '40px' }">
        <div class="login-header">
          <h2 class="title">自主學習導航系統</h2>
          <p class="subtitle">請登入您的帳號以繼續</p>
        </div>

        <el-form label-position="top" @keyup.enter="login">
          <el-form-item label="帳號">
            <el-input v-model="username" placeholder="請輸入帳號" :disabled="isLoading" />
          </el-form-item>
          
          <el-form-item label="密碼">
            <el-input 
              v-model="password" 
              type="password" 
              placeholder="請輸入密碼" 
              show-password 
              :disabled="isLoading" 
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
              <el-button link type="primary" @click="router.push('/register')" :disabled="isLoading">立即註冊</el-button>
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
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const isLoading = ref(false)

const login = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('請輸入帳號與密碼')
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL}/auth/login`, 
      { username: username.value, password: password.value },
      { withCredentials: true }
    );

    const { user_id, username: name } = response.data
    localStorage.setItem('user_id', user_id)
    localStorage.setItem('username', name)
    window.dispatchEvent(new Event('login'))
    
    ElMessage.success('登入成功！')
    router.push('/calendar') 
  } catch (err) {
    const errorMsg = err.response?.data?.error || '登入失敗，請檢查帳號密碼'
    ElMessage.error(errorMsg)
  } finally {
    if (router.currentRoute.value.path.includes('login')) {
        isLoading.value = false
    }
  }
}
</script>

<style scoped>
/* 背景與佈局 */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

/* 卡片樣式 */
.login-card {
  border-radius: 12px;
  border: 1px solid #ebeef5;
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
  margin: 0;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin-top: 10px;
}

.main-btn {
  width: 100%;
  height: 42px;
  margin-top: 10px;
  font-size: 16px;
  border-radius: 6px;
}

.footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #606266;
}

/* 提示文字區塊樣式 */
.notice-info {
  margin-top: 20px;
  opacity: 0.85;
}

/* 📱 手機響應式優化 (與 Register 統一) */
@media (max-width: 480px) {
  .login-wrapper {
    background-color: #ffffff; /* 手機版背景轉白，更像原生 App */
    align-items: flex-start;
    padding-top: 40px;
  }
  
  .login-card {
    border: none;
    box-shadow: none;
  }
  
  .login-container {
    max-width: 100%;
  }

  .title {
    font-size: 22px;
  }
}
</style>
