<template>
  <div class="review-container">
    <header class="header-card">
      <div class="top-row">
        <h2>🎯 錯題診斷與複習追蹤</h2>
        <div class="date-picker">
          <input type="date" v-model="filters.start" @change="fetchData" />
          <span class="date-sep">至</span>
          <input type="date" v-model="filters.end" @change="fetchData" />
        </div>
      </div>

      <nav class="subject-tabs">
        <button 
          v-for="s in subjects" :key="s.name"
          :class="['tab-btn', { active: currentSubject === s.name }]"
          @click="selectSubject(s.name)"
        >
          {{ s.icon }} {{ s.name }}
        </button>
      </nav>

      <div class="progress-section">
        <div class="progress-labels">
          <span>{{ currentSubject }}科 訂正進度 (不含滿分)</span>
          <span class="percentage">{{ correctionRate }}%</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: correctionRate + '%' }"></div>
        </div>
      </div>
    </header>

    <main class="list-section">
      <div v-if="loading" class="state-msg">🔄 資料讀取中...</div>
      <div v-else-if="records.length === 0" class="state-msg empty-full">
        🌟 太棒了！此區間沒有 {{ currentSubject }} 的錯題紀錄。
      </div>

      <div v-else class="record-grid">
        <div v-for="item in records" :key="item.id" 
             :class="['error-card', { 'is-done': item.is_corrected }]">
          
          <div class="check-zone" @click="toggleStatus(item)">
            <div :class="['check-box', { checked: item.is_corrected }]">
              <span v-if="item.is_corrected">✓</span>
            </div>
          </div>

          <div class="info-zone">
            <div class="info-header">
              <div class="header-left">
                <span class="unit-label">{{ item.unit }}</span>
                <span class="type-tag" :style="getTypeStyle(item.type)">{{ item.type }}</span>
              </div>
              
              <div class="header-right">
                <div class="score-badge">
                  <span class="score-val">{{ item.score }}</span>
                  <span class="score-unit">分</span>
                </div>
                <div class="date-badge">
                  <span class="calendar-icon">📅</span>
                  <span class="date-text">{{ item.date }}</span>
                </div>
              </div>
            </div>

            <p class="note-content">{{ item.clean_note }}</p>

            <div class="ai-insight-box" v-if="item.insight">
              <div class="ai-header">
                <div class="ai-avatar">✨</div>
                <span class="ai-title">AI 導師診斷</span>
                <el-button 
                  link 
                  @click="getAiDiagnose(item)" 
                  size="small" 
                  class="refresh-btn"
                  :loading="item.isAnalyzing"
                  :disabled="item.isAnalyzing"
                >重新分析</el-button>
              </div>
              <p class="ai-guidance">{{ item.insight }}</p>
            </div>

            <div v-else class="ai-trigger-zone">
              <el-button 
                class="magic-btn-el"
                :loading="item.isAnalyzing"
                :disabled="item.isAnalyzing"
                @click="getAiDiagnose(item)"
              >
                {{ item.isAnalyzing ? '🤖 AI 正在分析思考路徑中...' : '✨ 召喚 AI 老師深度分析觀念' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const subjects = [
  { name: '社會', icon: '📜' }, { name: '數學', icon: '🔢' },
  { name: '國語', icon: '✍️' }, { name: '自然', icon: '🧪' },
  { name: '英文', icon: '🔤' }
];

const currentSubject = ref('社會');
const loading = ref(false);
const records = ref([]);

// 🚀 動態日期初始化：讓日期選擇器預設顯示最近一個月
const today = new Date().toISOString().split('T')[0];
const oneMonthAgo = new Date();
oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
const startDate = oneMonthAgo.toISOString().split('T')[0];

const filters = reactive({ 
  start: startDate, 
  end: today 
});

const userId = parseInt(localStorage.getItem('user_id'));
const API_BASE = import.meta.env.VITE_API_BASE_URL;

const fetchData = async () => {
  loading.value = true;
  try {
    const res = await axios.get(`${API_BASE}/api/review/list`, {
      params: { 
        subject: currentSubject.value, 
        user_id: userId,
        start: filters.start, 
        end: filters.end 
      }
    });

    // 將後端的 ai_insight 映射到前端使用的 insight 欄位
    records.value = res.data.map(item => ({ ...item, isAnalyzing: false }));
  } catch (error) {
    console.error("讀取失敗:", error);
    ElMessage.error("讀取資料失敗");
  } finally {
    loading.value = false;
  }
};

const getAiDiagnose = async (row) => {
  if (row.isAnalyzing) return;
  row.isAnalyzing = true; 
  try {
    const res = await axios.post(`${API_BASE}/api/review/ai_diagnose`, {
      id: row.id, 
      subject: row.subject, 
      unit: row.unit, 
      note: row.clean_note, 
      user_id: userId
    });
    if (res.data.insight) {
      row.insight = res.data.insight;
      ElMessage.success("診斷完成！");
    }
  } catch (error) {
    ElMessage.error("分析失敗");
  } finally {
    row.isAnalyzing = false; 
  }
};

const selectSubject = (name) => { 
  currentSubject.value = name; 
  fetchData(); 
};

const toggleStatus = async (item) => {
  item.is_corrected = !item.is_corrected;
  try {
    await axios.post(`${API_BASE}/api/review/toggle`, { 
      id: item.id, 
      is_corrected: item.is_corrected 
    });
  } catch (e) {
    ElMessage.error("更新失敗");
  }
};

const correctionRate = computed(() => {
  if (!records.value.length) return 0;
  return Math.round((records.value.filter(r => r.is_corrected).length / records.value.length) * 100);
});

const getTypeStyle = (type) => {
  const styles = {
    '考卷': { background: '#FFF0F0', color: '#C92A2A' },
    '評量': { background: '#E7F5FF', color: '#1971C2' },
    '自修': { background: '#F8F9FA', color: '#495057' }
  };
  return styles[type] || { background: '#F3F0FF', color: '#6741D9' };
};

onMounted(fetchData);
</script>

<style scoped>
.review-container { 
  margin: 0 auto; padding: 20px; background: #f8f9fa; min-height: 100vh; display: flex; flex-direction: column; 
}

/* Header 佈局：標題與日期左右分開 */
.header-card { background: white; padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 25px; }
.top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.top-row h2 { margin: 0; font-size: 1.5rem; }

.date-picker { display: flex; align-items: center; gap: 10px; }
.date-picker input { padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 8px; font-size: 14px; color: #495057; outline: none; }
.date-sep { color: #adb5bd; font-size: 14px; }

/* 進度條 */
.progress-section { margin-top: 20px; }
.progress-labels { display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 600; color: #495057; }
.percentage { color: #339af0; }
.progress-track { height: 10px; background: #e9ecef; border-radius: 5px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #339af0, #22b8cf); transition: width 0.6s ease; }

/* 列表區塊 */
.list-section { flex-grow: 1; display: flex; flex-direction: column; }
.empty-full { flex-grow: 1; display: flex; align-items: center; justify-content: center; color: #adb5bd; font-size: 1.2rem; }
.record-grid { display: flex; flex-direction: column; gap: 15px; }

/* 卡片設計 */
.error-card { display: flex; background: white; border-radius: 16px; padding: 24px; border: 1px solid #eee; transition: transform 0.2s; }
.error-card:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.05); }

.info-zone { flex-grow: 1; padding-left: 20px; display: flex; flex-direction: column; }
.info-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.header-left { display: flex; gap: 10px; align-items: center; }

/* 右側分數與日期 */
.header-right { display: flex; flex-direction: row; align-items: flex-end; gap: 20px;  margin-left: auto; }
.score-badge { color: #fa5252; display: flex; align-items: baseline; }
.score-val { font-size: 1.6rem; font-weight: 900; line-height: 1; }
.score-unit { font-size: 0.85rem; font-weight: 700; margin-left: 2px; }
.date-badge { display: flex; align-items: center; gap: 6px; background: #f8f9fa; padding: 5px 12px; border-radius: 8px; border: 1px solid #e9ecef; white-space: nowrap;}
.date-text { color: #868e96; font-size: 13px; font-weight: 600; font-family: monospace;}

/* 標籤與內容 */
.unit-label { background: #e7f5ff; color: #1971c2; padding: 4px 12px; border-radius: 6px; font-weight: 700; }
.type-tag { font-size: 11px; padding: 2px 10px; border-radius: 50px; font-weight: 700; }
.note-content { font-size: 1.1rem; font-weight: 700; color: #212529; margin: 15px 0; line-height: 1.5; }

/* 召喚按鈕風格 (白色虛線) */
.magic-btn-el {
  width: 100%; height: 50px; background-color: #ffffff !important; border: 2px dashed #d0ebff !important;
  border-radius: 12px !important; color: #339af0 !important; font-weight: 700 !important; transition: all 0.3s;
}
.magic-btn-el.is-disabled { background-color: #f8f9fa !important; border: 2px solid #dee2e6 !important; color: #adb5bd !important; }

/* AI 診斷區塊 */
.ai-insight-box { 
  background: #fdfcfe; border-radius: 12px; padding: 18px; margin-top: 15px; border: 1px solid #f3f0ff; position: relative;
}
.ai-insight-box::before { 
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background: linear-gradient(180deg, #339af0, #9775fa); 
}
.ai-title { font-size: 15px; font-weight: 800; color: #5f3dc4; }
.ai-guidance { font-size: 15px; line-height: 1.7; color: #495057; }

/* Tab 與 Checkbox */
.subject-tabs { display: flex; gap: 10px; margin-bottom: 25px; }
.tab-btn { padding: 12px 20px; border: none; border-radius: 12px; background: #f1f3f5; cursor: pointer; font-weight: 700; }
.tab-btn.active { background: #339af0; color: white; }
.check-box { width: 30px; height: 30px; border: 2px solid #dee2e6; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.check-box.checked { background: #40c057; border-color: #40c057; color: white; }
.refresh-btn { margin-left: auto; color: #adb5bd !important; }

/* ==========================================================================
   手機版 RWD 優化 (僅在 768px 以下生效)
   ========================================================================== */
@media (max-width: 768px) {
  .review-container {
    padding: 10px !important;
    background: #ffffff !important; /* 洗白背景 */
  }

  /* 1. Header 佈局調整：將日期與標題垂直排列 */
  .header-card {
    padding: 15px !important;
    margin-bottom: 15px !important;
    border-radius: 12px !important;
  }

  .top-row {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 15px;
  }

  .top-row h2 {
    font-size: 1.25rem !important;
  }

  .date-picker {
    width: 100%;
    justify-content: space-between;
  }

  .date-picker input {
    flex: 1;
    width: 40%; /* 確保兩個 input 不會擠在一起 */
    font-size: 13px !important;
    padding: 6px !important;
  }

  /* 2. 科目分頁：改為橫向滑動 (解決按鈕換行問題) */
  .subject-tabs {
    overflow-x: auto;
    white-space: nowrap;
    padding-bottom: 10px;
    gap: 8px !important;
    -webkit-overflow-scrolling: touch;
  }

  .subject-tabs::-webkit-scrollbar {
    display: none; /* 隱藏捲動條讓畫面更乾淨 */
  }

  .tab-btn {
    flex: 0 0 auto; /* 防止按鈕被壓縮 */
    padding: 8px 16px !important;
    font-size: 14px !important;
  }

  /* 3. 卡片佈局重組：解決資訊擠壓 */
  .error-card {
    padding: 15px !important;
    flex-direction: column !important; /* 手機版將 Checkbox 置於頂部或左側 */
    position: relative;
  }

  .info-zone {
    padding-left: 0 !important;
    margin-top: 10px;
  }

  .info-header {
    flex-direction: column; /* 讓標籤與分數/日期垂直分開 */
    gap: 10px;
  }

  .header-left {
    flex-wrap: wrap; /* 標籤太長時可換行 */
  }

  /* 4. 分數與日期：在手機版改為並排靠左 */
  .header-right {
    width: 100%;
    justify-content: flex-start !important;
    align-items: center !important;
    gap: 15px !important;
    margin-top: 5px;
  }

  .score-val {
    font-size: 1.4rem !important;
  }

  .date-badge {
    padding: 3px 8px !important;
  }

  /* 5. 內容字體微調 */
  .note-content {
    font-size: 1rem !important;
    margin: 10px 0 !important;
  }

  /* 6. AI 診斷區塊優化 */
  .ai-insight-box {
    padding: 12px !important;
  }

  .ai-guidance {
    font-size: 14px !important;
    line-height: 1.6 !important;
  }

  .magic-btn-el {
    height: 44px !important;
    font-size: 14px !important;
  }

  /* 7. Checkbox 樣式調整：固定在右上方 */
  .check-zone {
    position: absolute;
    right: 15px;
    top: 15px;
  }
}
</style>