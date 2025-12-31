<template>
  <div class="login-wrapper">
    <el-card class="login-card" :body-style="{ padding: '40px' }">
      <div class="login-header">
        <h2 class="title">自學管理系統</h2>
        <p class="subtitle">請登入您的帳號以繼續</p>
      </div>

      <el-form label-position="top">
        <el-form-item label="帳號">
          <el-input v-model="username" placeholder="Username" />
        </el-form-item>
        
        <el-form-item label="密碼">
          <el-input v-model="password" type="password" placeholder="Password" show-password />
        </el-form-item>

        <div class="button-group">
          <el-button type="primary" @click="login" class="main-btn">登入</el-button>
          <div class="footer">
            <span>沒有帳號嗎？</span>
            <el-button link type="primary" @click="$router.push('/register')">立即註冊</el-button>
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
// 1. 這裡定義的是 username 和 password
const username = ref('')
const password = ref('')

const login = async () => {
  try {
    const response = await axios.post(
      `${import.meta.env.VITE_API_BASE_URL}/auth/login`, 
      {
        // 2. 修正：直接使用 username.value (原本寫成 form.value)
        username: username.value,
        password: password.value
      },
      {
        withCredentials: true 
      }
    );

    // 3. 修正：使用 response.data (原本寫成 res.data)
    const { user_id, username: name } = response.data
    
    localStorage.setItem('user_id', user_id)
    localStorage.setItem('username', name)
    
    // 通知全域登入事件
    window.dispatchEvent(new Event('login'))

    console.log("登入成功，user_id =", user_id)
    ElMessage.success('登入成功')
    
    // 跳轉
    router.push('/calendar') 
    
  } catch (err) {
    // 4. 修正：失敗時不要印 user_id，因為它不存在
    console.error("登入失敗內容 =", err.response?.data || err.message)
    ElMessage.error('登入失敗，請檢查帳號密碼')
  }
}
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa; /* 極淺灰背景，突顯白色卡片 */
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* 柔和陰影 */
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



