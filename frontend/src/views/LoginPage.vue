<template>
  <div 
    class="login-wrapper" 
    v-loading="isLoading"
    element-loading-text="正在登入，請稍候..."
    element-loading-background="rgba(255, 255, 255, 0.7)"
  >
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

// 3. 定義 loading 狀態變數
const isLoading = ref(false)

const login = async () => {
  // 防止空白登入
  if (!username.value || !password.value) {
    ElMessage.warning('請輸入帳號與密碼')
    return
  }

  isLoading.value = true // 開啟 Loading
  
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

    const { user_id, username: name } = response.data
    
    localStorage.setItem('user_id', user_id)
    localStorage.setItem('username', name)
    
    window.dispatchEvent(new Event('login'))

    console.log("登入成功，使用者 ID:", user_id)
    ElMessage.success('登入成功！正在跳轉...')
    
    router.push('/calendar') 
    
  } catch (err) {
    console.error("登入失敗詳情 =", err.response?.data || err.message)
    const errorMsg = err.response?.data?.error || '登入失敗，請檢查帳號密碼'
    ElMessage.error(errorMsg)
  } finally {
    // 4. 無論成功或失敗，最後都要關閉 Loading (若成功跳轉則不影響)
    // 為了防止跳轉瞬間畫面閃爍，可以留著 isLoading 直到路由跳轉
    if (router.currentRoute.value.path === '/login') {
        isLoading.value = false
    }
  }
}
</script>
