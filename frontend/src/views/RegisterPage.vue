<template>
  <div class="register-wrapper">
    <div class="register-container">
      <el-card class="register-card" :body-style="{ padding: '40px' }">
        <div class="register-header">
          <h2 class="title">建立新帳號</h2>
          <p class="subtitle">加入自主學習導航系統，開啟智慧學習之旅</p>
        </div>

        <el-form label-position="top" @keyup.enter="handleRegister">
          <el-form-item label="帳號">
            <el-input 
              v-model="form.username" 
              placeholder="請輸入帳號" 
              prefix-icon="User"
              :disabled="loading"
            />
          </el-form-item>

          <el-form-item label="學生年級">
            <el-select v-model="form.grade" placeholder="請選擇年級" style="width: 100%" :disabled="loading">
              <el-option label="一年級" :value="1" />
              <el-option label="二年級" :value="2" />
              <el-option label="三年級" :value="3" />
              <el-option label="四年級" :value="4" />
              <el-option label="五年級" :value="5" />
              <el-option label="六年級" :value="6" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="密碼">
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="請輸入密碼" 
              show-password 
              prefix-icon="Lock"
              :disabled="loading"
            />
          </el-form-item>

          <el-form-item label="確認密碼">
            <el-input 
              v-model="confirmPassword" 
              type="password" 
              placeholder="請再次輸入密碼" 
              show-password 
              prefix-icon="Checked"
              :disabled="loading"
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
              <el-button link type="primary" @click="router.push('/login')" :disabled="loading">返回登入</el-button>
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
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
// 1. 導入統一封裝的 request
import request from '@/api/request';

const router = useRouter();
const form = ref({ 
  username: '', 
  password: '', 
  grade: 1 
});
const confirmPassword = ref('');
const loading = ref(false);

const handleRegister = async () => {
  if (!form.value.username || !form.value.password || !form.value.grade) {
    return ElMessage.warning('請填寫完整資訊');
  }

  if (form.value.password !== confirmPassword.value) {
    return ElMessage.error('兩次輸入的密碼不一致');
  }

  loading.value = true;
  try {
    // 2. 使用封裝後的 request，移除硬編碼網址
    // 注意：request.js 的攔截器已經處理過 response.data，所以這裡直接拿回傳結果
    await request.post('/auth/register', {
      username: form.value.username,
      password: form.value.password,
      grade: form.value.grade
    });

    ElMessage.success('註冊成功！請登入');
    router.push('/login');
  } catch (error) {
    // 錯誤訊息由 request.js 的攔截器統一處理彈出，此處僅處理 loading
    console.error('註冊錯誤:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 基礎佈局與 Login 保持一致 */
.register-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 400px;
}

.register-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.register-header {
  text-align: center;
  margin-bottom: 25px;
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
  line-height: 1.4;
}

.main-btn {
  width: 100%;
  height: 44px;
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

.notice-info {
  margin-top: 20px;
}

/* 移除 Element Plus Form Item 的底部間距 */
:deep(.el-form-item) {
  margin-bottom: 20px;
}

/* 📱 手機相容界面優化 (RWD) */
@media (max-width: 480px) {
  .register-wrapper {
    background-color: #ffffff; /* 手機版背景轉白 */
    align-items: flex-start;
    padding-top: 40px;
  }
  
  .register-card {
    border: none;
    box-shadow: none;
  }
  
  .register-container {
    max-width: 100%;
  }

  .title {
    font-size: 22px;
  }

  /* 手機上表單間距稍大，避免誤觸 */
  :deep(.el-form-item) {
    margin-bottom: 22px;
  }
}
</style>