<template>
  <el-card class="settings-card">
    <template #header>
      <div class="custom-header">
        <div class="title-section">
          <span class="title-icon">⚙️</span>
          <span class="title-text">學習版本與時程設定</span>
        </div>
        <div class="action-section">
          <el-button 
            class="save-btn" 
            type="primary" 
            @click="saveAllSettings" 
            :loading="saving"
          >
            <el-icon v-if="!saving" style="margin-right: 8px;"><Check /></el-icon>
            儲存所有設定
          </el-button>
        </div>
      </div>
    </template>

    <div class="global-settings-section">
      <h3 class="section-title">🗓️ 學期重要時程</h3>
      <el-row :gutter="40">
        <el-col :span="12">
          <div class="date-picker-wrap">
            <span class="label">期中考日期：</span>
            <el-date-picker v-model="globalDates.midterm_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            <div class="input-hint">建議設定為段考的 <strong>最後一天</strong></div>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="date-picker-wrap">
            <span class="label">期末考日期：</span>
            <el-date-picker v-model="globalDates.final_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            <div class="input-hint">建議設定為段考的 <strong>最後一天</strong></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-divider />

    <div class="global-settings-section">
      <h3 class="section-title">🤖 AI 智能助理配置</h3>
      <el-form :model="aiConfig" label-position="top">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="Gemini API Key">
              <el-input v-model="aiConfig.api_key" type="password" show-password placeholder="請輸入 API Key (如 AIzaSy...)" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="模型名稱">
              <el-select v-model="aiConfig.model_name" style="width: 100%">
                <el-option label="Gemini 1.5 Flash (推薦)" value="gemini-1.5-flash" />
                <el-option label="Gemini 1.5 Pro" value="gemini-1.5-pro" />
                <el-option label="Gemini 2.0 Flash (實驗)" value="gemini-2.0-flash-exp" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="AI 教師人格 (System Prompt / 關鍵字)">
          <el-input 
            v-model="aiConfig.system_prompt" 
            type="textarea" 
            :rows="3" 
            placeholder="例如：你是一位有耐心的國小老師..." 
          />
          <div class="input-hint">這會決定 AI 說話的語氣與輔導風格</div>
        </el-form-item>
      </el-form>
    </div>

    <el-divider />

    <h3 class="section-title">📘 各科版本設定</h3>
    <el-table :data="localConfigs" style="width: 100%" stripe>
      <el-table-column prop="subject_name" label="科目" width="140">
        <template #default="scope">
          <span class="subject-text">{{ scope.row.subject_name }}</span>
        </template>
      </el-table-column>
      
      <el-table-column label="年級" width="200">
        <template #default="scope">
          <el-select v-model="scope.row.grade" placeholder="選擇年級" class="large-select">
            <el-option v-for="g in grades" :key="g.val" :label="g.label" :value="g.val" />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column label="出版社版本">
        <template #default="scope">
          <el-radio-group v-model="scope.row.publisher" size="large" class="publisher-radio">
            <el-radio-button value="康軒">康軒</el-radio-button>
            <el-radio-button value="翰林">翰林</el-radio-button>
            <el-radio-button value="南一">南一</el-radio-button>
          </el-radio-group>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="footer-hint">
      💡 AI 老師將根據此設定提供最精確的輔導內容，考期設定將幫助您追蹤學習進度
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'

// 從 localStorage 取得 user_id，請確保登入時有存入
const userId = localStorage.getItem('user_id')
const saving = ref(false)

const subjects = ['國語', '數學', '社會', '自然', '英文']
const grades = [
  { val: 1, label: '一年級' }, { val: 2, label: '二年級' }, { val: 3, label: '三年級' },
  { val: 4, label: '四年級' }, { val: 5, label: '五年級' }, { val: 6, label: '六年級' },
  { val: 7, label: '七年級 (國一)' }, { val: 8, label: '八年級 (國二)' }, { val: 9, label: '九年級 (國三)' }
]

const localConfigs = ref(subjects.map(s => ({ subject_name: s, publisher: '康軒', grade: 6 })))
const globalDates = ref({ midterm_date: '', final_date: '' })

const aiConfig = ref({
  api_key: '',
  system_prompt: '',
  model_name: 'gemini-1.5-flash',
  base_url: 'https://generativelanguage.googleapis.com/v1beta'
})

const loadSettings = async () => {
  if (!userId) return
  try {
    // 1. 載入版本與科目
    const resPub = await axios.get(`http://localhost:5000/api/config/publishers?user_id=${userId}`)
    if (resPub.data && resPub.data.length > 0) localConfigs.value = resPub.data

    // 2. 載入全域考期
    const resGlobal = await axios.get(`http://localhost:5000/api/config/global?user_id=${userId}`)
    if (resGlobal.data) {
      globalDates.value.midterm_date = resGlobal.data.midterm_date || ''
      globalDates.value.final_date = resGlobal.data.final_date || ''
    }

    // 3. 載入 AI 配置
    const resAI = await axios.get(`http://localhost:5000/api/config/ai?user_id=${userId}`)
    if (resAI.data && resAI.data.api_key) {
      aiConfig.value = { ...aiConfig.value, ...resAI.data }
    }
  } catch (err) {
    console.error("載入失敗:", err)
    // 注意：如果後端沒開，這裡會報 Network Error
  }
}

const saveAllSettings = async () => {
  if (!userId) {
    ElMessage.warning('無法識別使用者，請重新登入')
    return
  }
  
  saving.value = true
  try {
    // A. 儲存各科版本
    await axios.post('http://localhost:5000/api/config/publishers', {
      user_id: userId,
      configs: localConfigs.value
    })

    // B. 儲存全域考期
    const currentGrade = localConfigs.value[0]?.grade || 6
    await axios.post('http://localhost:5000/api/config/global', {
      user_id: userId,
      grade: currentGrade,
      midterm_date: globalDates.value.midterm_date,
      final_date: globalDates.value.final_date
    })

    // C. 儲存 AI 配置
    await axios.post('http://localhost:5000/api/config/ai', {
      user_id: userId,
      ...aiConfig.value
    })

    // 同步到 LocalStorage 供前端其他頁面即時使用
    localStorage.setItem('midterm_date', globalDates.value.midterm_date || '')
    localStorage.setItem('final_date', globalDates.value.final_date || '')
    localStorage.setItem('user_grade', currentGrade)

    ElMessage.success('所有設定與 AI 配置已成功同步')
  } catch (err) {
    console.error("儲存失敗:", err)
    ElMessage.error('儲存失敗，請檢查後端連線')
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
</script>

<style scoped>
.custom-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 5px; }
.title-section { display: flex; align-items: center; }
.title-icon { font-size: 1.8rem; margin-right: 12px; }
.title-text { font-size: 1.6rem; font-weight: 800; color: #2c3e50; }

.global-settings-section {
  padding: 20px;
  background-color: #fcfdfe;
  border-radius: 16px;
  border: 1px solid #f0f2f5;
  margin-bottom: 10px;
}

.section-title { font-size: 1.3rem; font-weight: 700; color: #409eff; margin-bottom: 20px; }
.date-picker-wrap { display: flex; flex-direction: column; gap: 10px; }
.label { font-weight: 600; color: #606266; }

.save-btn {
  height: 50px !important;
  padding: 0 35px !important;
  font-size: 1.2rem !important;
  font-weight: bold;
  border-radius: 25px !important;
  background: linear-gradient(135deg, #409eff 0%, #3a8ee6 100%) !important;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
}

.settings-card { margin: 20px auto; border-radius: 24px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }

:deep(.el-form-item__label) { font-weight: 700; color: #5d6d7e; font-size: 1.05rem; }
:deep(.el-input__wrapper), :deep(.el-textarea__inner) { border-radius: 12px !important; padding: 8px 15px; }

.subject-text { font-size: 1.2rem; font-weight: 700; color: #444; }
:deep(.el-table) { border-radius: 16px; overflow: hidden; margin-top: 10px; }
.input-hint { margin-top: 8px; font-size: 0.9rem; color: #909399; display: flex; align-items: center; }
.input-hint::before { content: '💡'; margin-right: 5px; }
.footer-hint { margin: 30px 0; font-size: 1.1rem; color: #a8abb2; text-align: center; font-style: italic; }
</style>