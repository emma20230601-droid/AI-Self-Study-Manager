<template>
  <div class="register-wrapper">
    <el-card class="register-card" :body-style="{ padding: '40px' }">
      <div class="register-header">
        <h2 class="title">建立新帳號</h2>
        <p class="subtitle">加入自學管理系統，開啟智慧學習之旅</p>
      </div>

      <el-form label-position="top">
        <el-form-item label="帳號">
          <el-input 
            v-model="form.username" 
            placeholder="請輸入帳號" 
          />
        </el-form-item>
        
        <el-form-item label="密碼">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="請輸入密碼" 
            show-password 
          />
        </el-form-item>

        <el-form-item label="確認密碼">
          <el-input 
            v-model="confirmPassword" 
            type="password" 
            placeholder="請再次輸入密碼" 
            show-password 
          />
        </el-form-item>

        <div class="button-group">
          <el-button 
            type="primary" 
            @click="handleRegister" 
            class="main-btn" 
            :loading="loading"
          >
            立即註冊
          </el-button>
          <div class="footer">
            <span>已經有帳號了？</span>
            <el-button link type="primary" @click="router.push('/login')">返回登入</el-button>
          </div>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const router = useRouter();
const form = ref({ username: '', password: '' });
const confirmPassword = ref('');
const loading = ref(false);

const handleRegister = async () => {
  // 1. 基本內容檢查
  if (!form.value.username || !form.value.password) {
    return ElMessage.warning('請填寫完整帳號與密碼');
  }

  // 2. 密碼一致性檢查
  if (form.value.password !== confirmPassword.value) {
    return ElMessage.error('兩次輸入的密碼不一致');
  }

  loading.value = true;
  try {
    // 發送到後端 auth 路由
    const response = await axios.post('${import.meta.env.VITE_API_BASE_URL}/auth/register', {
      username: form.value.username,
      password: form.value.password
    });

    if (response.status === 201) {
      ElMessage.success('註冊成功！請登入');
      router.push('/login');
    }
  } catch (error) {
    // 優先抓取後端回傳的 error 欄位
    const errorMsg = error.response?.data?.error || '註冊失敗，請稍後再試';
    ElMessage.error(errorMsg);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-wrapper {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa; /* 淺灰背景突顯白色卡片 */
}

.register-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.register-header {
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

/* 移除 Element Plus Form Item 的底部間距，讓排版更緊湊 */
:deep(.el-form-item) {
  margin-bottom: 18px;
}

</style>

