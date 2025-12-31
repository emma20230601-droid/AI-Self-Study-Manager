<template>
  <div class="login-wrapper">
    <el-card class="login-card" :body-style="{ padding: '40px' }">
      <div class="login-header">
        <h2 class="title">自學管理系統</h2>
        <p class="subtitle">請登入您的帳號以繼續</p>
      </div>

      <el-form label-position="top">
        <el-form-item label="帳號">
          <el-input v-model="username" placeholder="請輸入帳號" />
        </el-form-item>
        
        <el-form-item label="密碼">
          <el-input v-model="password" type="password" placeholder="請輸入密碼" show-password />
        </el-form-item>

        <div class="button-group">
          <el-button type="primary" @click="login" class="main-btn">登入</el-button>
          <div class="footer">
            <span>沒有帳號嗎？</span>
            <el-button link type="primary" @click="router.push('/register')">立即註冊</el-button>
          </div>
        </div>
      </el-form>
    </el-card>
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

const login = async () => {
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL}/auth/login`, 
      {
        username: username.value,
        password: password.value
      },
      {
        withCredentials: true 
      }
    );

    // 取得後端回傳的使用者資訊
    const { user_id, username: name } = response.data
    
    // 存入瀏覽器快取
    localStorage.setItem('user_id', user_id)
    localStorage.setItem('username', name)
    
    // 發送全域登入事件通知導航欄或其他組件更新
    window.dispatchEvent(new Event('login'))

    console.log("登入成功，使用者 ID:", user_id)
    ElMessage.success('登入成功！正在跳轉...')
    
    // 成功後跳轉至行事曆/主頁面
    router.push('/calendar') 
    
  } catch (err) {
    // 錯誤處理：詳細紀錄錯誤內容，但不讓程式崩潰
    console.error("登入失敗詳情 =", err.response?.data || err.message)
    const errorMsg = err.response?.data?.error || '登入失敗，請檢查帳號密碼'
    ElMessage.error(errorMsg)
  }
}
</script>

<style scoped>
/* 保持你原本精美的 CSS 排版 */
.login-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 400px;
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
  height: 40px;
  margin-top: 10px;
  font-size: 15px;
  border-radius: 6px;
}

.footer {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: #606266;
}
</style>
