<template>
  <div class="full-page-container">
    <el-card class="settings-card-full">
      <template #header>
        <div class="custom-header">
          <h2 class="title-text">⚙️ 學習版本與時程設定</h2>
        </div>
      </template>

      <div class="settings-section">
        <h3 class="section-title">🗓️ 學期重要時程</h3>
        <el-row :gutter="40">
          <el-col :xs="24" :sm="12">
            <div class="input-wrap">
              <span class="label-text">期中考日期：</span>
              <el-date-picker v-model="globalDates.midterm_date" type="date" value-format="YYYY-MM-DD" size="large" style="width: 100%" />
            </div>
          </el-col>
          <el-col :xs="24" :sm="12">
            <div class="input-wrap">
              <span class="label-text">期末考日期：</span>
              <el-date-picker v-model="globalDates.final_date" type="date" value-format="YYYY-MM-DD" size="large" style="width: 100%" />
            </div>
          </el-col>
        </el-row>
      </div>

      <el-divider />

      <div class="settings-section">
        <h3 class="section-title">🤖 AI 智能助理配置</h3>
        <el-form :model="aiConfig" label-position="top">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="14">
              <el-form-item label="Gemini API Key">
                <el-input v-model="aiConfig.api_key" type="password" show-password size="large" placeholder="請輸入 API Key" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="10">
              <el-form-item label="模型名稱">
                <el-select v-model="aiConfig.model_name" size="large" style="width: 100%">
                  <el-option label="Gemini 2.5 Flash" value="gemini-2.5-flash" />
                  <el-option label="Gemini 1.5 Flash" value="gemini-1.5-flash" />
                  <el-option label="Gemini 1.5 Pro" value="gemini-1.5-pro" />
                  <el-option label="Gemini 2.0 Flash (實驗)" value="gemini-2.0-flash-exp" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="快速套用教學風格 (點擊下方按鈕可快速產生指令)">
        <el-radio-group v-model="tempPersonality" size="large" @change="applyTemplate">
          <el-radio-button value="expert">🔴 精簡專家模式 (講重點)</el-radio-button>
          <el-radio-button value="gentle">🟢 溫柔引導模式 (說故事)</el-radio-button>
        </el-radio-group>
      </el-form-item>

          <el-form-item label="AI 教師自定義人格指令 (System Prompt)">
        <el-input 
          v-model="aiConfig.system_prompt" 
          type="textarea" 
          :rows="6" 
          placeholder="請輸入或從上方選擇風格後修改..."
          style="font-size: 1.2rem"
        />
        <div class="hint-text">最終以此輸入框的內容作為 AI 的行為準則。</div>
      </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <div class="settings-section">
        <h3 class="section-title">📘 各科版本設定</h3>
        <el-table :data="localConfigs" style="width: 100%" stripe class="large-font-table">
          <el-table-column prop="subject_name" label="科目" width="120">
            <template #default="scope">
              <span class="subject-text">{{ scope.row.subject_name }}</span>
            </template>
          </el-table-column>
          
          <el-table-column label="年級" min-width="150">
            <template #default="scope">
              <el-select v-model="scope.row.grade" size="large">
                <el-option v-for="g in grades" :key="g.val" :label="g.label" :value="g.val" />
              </el-select>
            </template>
          </el-table-column>

          <el-table-column label="出版社版本" min-width="200">
            <template #default="scope">
              <el-radio-group v-model="scope.row.publisher" size="large">
                <el-radio-button value="康軒">康軒</el-radio-button>
                <el-radio-button value="翰林">翰林</el-radio-button>
                <el-radio-button value="南一">南一</el-radio-button>
              </el-radio-group>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="footer-actions">
        <el-button class="save-btn" type="primary" @click="saveAllSettings" :loading="saving">
          <el-icon v-if="!saving" style="margin-right: 8px;"><Check /></el-icon>
          儲存所有設定
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'

const userId = localStorage.getItem('user_id')
const saving = ref(false)

// ✨ 從 localStorage 讀取註冊時存下的年級
const savedGrade = localStorage.getItem('user_grade')
const userGrade = savedGrade ? parseInt(savedGrade) : 6
console.log("當前 LocalStorage 中的年級是:", savedGrade) // <--- 打開控制台看看這行印出什麼

const subjects = ['國語', '數學', '社會', '自然', '英文']
const grades = [
  { val: 1, label: '一年級' }, { val: 2, label: '二年級' }, { val: 3, label: '三年級' },
  { val: 4, label: '四年級' }, { val: 5, label: '五年級' }, { val: 6, label: '六年級' }
]

// ✨ 初始化：修正變數名為 grade (非 grades)
const localConfigs = ref(subjects.map(s => ({ 
  subject_name: s, 
  publisher: '康軒', 
  grade: userGrade 
})))

const globalDates = ref({ midterm_date: '', final_date: '' })
const aiConfig = ref({ 
  api_key: '', 
  system_prompt: '', 
  model_name: 'gemini-2.5-flash',
  ai_personality: 'expert'
})

// ✨ 新增一個暫存按鈕狀態的變數，不一定要存進後端
const tempPersonality = ref('')


// ✨ 在 script setup 中定義模板
const promptTemplates = {
  expert: `你是一位精通台灣國小教材的專業導師。
【核心準則】：
1. 嚴格對齊：必須根據使用者提供的『年級』與『出版社版本』之單元架構進行診斷。
2. 風格：🔴 精簡專家模式。語氣冷靜專業，不使用冗長贅字，直擊問題核心。
3. 診斷要求：
   ● 定位錯誤：直接指出錯誤的知識點或邏輯缺漏。
   ● 解題步驟：提供邏輯嚴密、分步驟的正確解法。
   ● 教材關聯：簡短說明此問題對應該版本的哪一個重點觀念（例如：康軒版除法單元）。
4. 呈現方式：強制使用『列點』或『短句』，確保資訊密度高且易於閱讀。`,

  gentle: `你是一位精通台灣國小教材的專業導師。
【核心準則】：
1. 嚴格對齊：必須根據使用者提供的『年級』與『出版社版本』之單元架構進行診斷。
2. 風格：🟢 溫柔引導模式。語氣鼓勵且充滿耐心，將抽象觀念轉化為生活故事。
3. 詞彙限制：僅限國小程度，遇到抽象概念請用『生活中的例子』類比。
4. 診斷要求：
   ● 情感支持：先肯定學生的努力與嘗試。
   ● 啟發提問：不直接給答案，透過提問引導學生自行發現錯誤。
5. 呈現方式：多用分行與列點，單次回答不超過 150 字，多使用鼓勵性表情符號。`
}

// ✨ 點擊按鈕時的邏輯
const applyTemplate = (val) => {
  if (promptTemplates[val]) {
    // 直接把包含「嚴格參考年級與版本」的指令填入輸入框
    aiConfig.value.system_prompt = promptTemplates[val]
    ElMessage.info('已套用教學模板，包含年級與版本參考指令')
  }
}

const loadSettings = async () => {
  if (!userId) return
  try {
    // 1. 先抓取各科設定 (這是在 subject_configs 表格)
    const resPub = await axios.get(`http://localhost:5000/api/config/publishers?user_id=${userId}`)
    
    if (resPub.data && resPub.data.length > 0) {
      // ✅ 如果資料庫有各科紀錄，以資料庫為準
      localConfigs.value = resPub.data
      // 同步更新 LocalStorage，修正之前錯誤的暫存
      localStorage.setItem('user_grade', resPub.data[0].grade)
    } else {
      // 2. ❗ 如果各科沒紀錄 (新用戶)，我們需要從 User 表格抓取註冊年級
      // 假設你修正了後端，提供一個抓取用戶基本資料的 API
      try {
        const resUser = await axios.get(`http://localhost:5000/api/config/user_info?user_id=${userId}`)
        if (resUser.data && resUser.data.grade) {
          const dbGrade = resUser.data.grade
          // 套用到所有科目
          localConfigs.value.forEach(item => item.grade = dbGrade)
          localStorage.setItem('user_grade', dbGrade) // 修正暫存
        }
      } catch (userErr) {
        console.warn("無法從資料庫獲取初始年級，使用暫存值")
      }
    }

    const resGlobal = await axios.get(`http://localhost:5000/api/config/global?user_id=${userId}`)
    if (resGlobal.data) {
      globalDates.value = { 
        midterm_date: resGlobal.data.midterm_date || '', 
        final_date: resGlobal.data.final_date || '' 
      }
    }

    const resAI = await axios.get(`http://localhost:5000/api/config/ai?user_id=${userId}`)
    if (resAI.data && resAI.data.api_key) {
      aiConfig.value = { ...aiConfig.value, ...resAI.data }
    }
  } catch (err) {
    console.error("載入失敗", err)
  }
}


const saveAllSettings = async () => {
  if (!userId) return
  saving.value = true
  try {
    // 1. 儲存出版社與年級
    await axios.post('http://localhost:5000/api/config/publishers', { 
      user_id: userId, 
      configs: localConfigs.value 
    })

    // 2. 儲存全域設定
    await axios.post('http://localhost:5000/api/config/global', { 
      user_id: userId, 
      grade: localConfigs.value[0].grade, 
      midterm_date: globalDates.value.midterm_date,
      final_date: globalDates.value.final_date
    })

    // 3. 儲存 AI 配置
    await axios.post('http://localhost:5000/api/config/ai', { 
      user_id: userId, 
      ...aiConfig.value 
    })

    ElMessage.success('系統設定已成功更新')
  } catch (err) {
    ElMessage.error('儲存失敗')
  } finally {
    saving.value = false
  }
}

onMounted(loadSettings)
</script>

<style scoped>
.full-page-container { width: 100%; min-height: 100vh; background-color: #fff; }
.settings-card-full { border: none; border-radius: 0; box-shadow: none; }
.custom-header { padding: 20px 40px; text-align: left; border-bottom: 1px solid #f0f0f0; }
.title-text { font-size: 2.2rem; font-weight: 800; color: #303133; margin: 0; }
.settings-section { padding: 30px 40px; text-align: left; }
.section-title { font-size: 1.6rem; color: #409eff; margin-bottom: 25px; font-weight: bold; }
.label-text { display: block; margin-bottom: 10px; font-weight: bold; font-size: 1.2rem; color: #606266; }
.footer-actions { padding: 20px 40px 60px 40px; text-align: left; }
.save-btn { height: 65px !important; padding: 0 60px !important; font-size: 1.5rem !important; border-radius: 12px !important; font-weight: bold; }
.subject-text { font-size: 1.4rem; font-weight: 900; }

@media (max-width: 768px) {
  .settings-section { padding: 20px; }
  .footer-actions { padding: 20px; }
  .save-btn { width: 100%; }
}

:deep(.el-form-item__label) { font-size: 1.3rem !important; font-weight: bold !important; color: #333 !important; }
:deep(.el-input__inner), :deep(.el-select .el-input__inner) { font-size: 1.2rem !important; height: 50px; }
:deep(.el-table .cell) { font-size: 1.2rem; padding: 15px 0; }
</style>