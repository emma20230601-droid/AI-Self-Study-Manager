<template>
  <div class="teacher-dashboard">
    <header class="admin-header">
      <div class="title-zone">
        <h1>👨‍🏫 AI 教師教學診斷看板</h1>
        <p>分析對象：{{ currentSubject }} 學習表現</p>
      </div>
      
      <div class="filter-controls">
        <div class="date-group">
          <input type="date" v-model="filters.start" @change="fetchAnalysis" />
          <span>至</span>
          <input type="date" v-model="filters.end" @change="fetchAnalysis" />
        </div>
        <el-select v-model="currentSubject" @change="fetchAnalysis" class="subject-select" placeholder="選擇科目">
          <el-option v-for="s in ['社會','數學','國語','自然','英文']" :key="s" :label="s" :value="s" />
        </el-select>
      </div>
    </header>

    <section class="overview-grid">
      <div class="stat-card">
        <div class="label">平均掌握度</div>
        <div class="value">{{ analysis.summary?.avg_score || 0 }}%</div>
        <div class="trend">所選區間共 {{ analysis.summary?.total_count || 0 }} 次測驗</div>
      </div>
      <div class="stat-card warning">
        <div class="label">待補救次數</div>
        <div class="value">{{ analysis.summary?.failed_count || 0 }}</div>
        <div class="trend">得分低於 90 分項目</div>
      </div>
    </section>

    <section class="concept-analysis">
      <h3>🔴 待強化觀念清單 (根據錯題紀錄整理)</h3>
      <div v-if="weakUnits.length > 0" class="weak-list">
        <div v-for="item in weakUnits" :key="item.unit" class="weak-item">
          <div class="weak-info">
            <span class="weak-unit">📍 {{ item.unit }}</span>
            <span class="weak-count">出現 {{ item.count }} 次錯誤</span>
          </div>
          <div class="weak-advice">
            建議：此單元平均分數為 {{ item.avg }}%，需重新複習相關內容。
          </div>
        </div>
      </div>
      <div v-else class="empty-state">✨ 太棒了！此區間暫無明顯薄弱觀念。</div>
    </section>

    <section class="action-zone" v-if="analysis.summary?.total_count > 0">
      <button @click="generateAIQuiz" :disabled="generating" class="ai-btn">
        {{ generating ? '🤖 AI 正在分析錯題並出題中...' : '🪄 一鍵生成個人化補救考卷' }}
      </button>
      
      <div v-if="quizResult" class="quiz-display-card">
        <div class="quiz-header">
          <span>📝 AI 針對您的錯題生成：{{ currentSubject }} 補救教材</span>
          <button @click="quizResult = ''" class="close-btn">關閉</button>
        </div>
        <pre class="quiz-body">{{ quizResult }}</pre>
        <div class="quiz-footer">
          <el-button type="success" size="small" @click="copyToClipboard">複製內容</el-button>
          <small>💡 提示：AI 已讀取您最近的實體錯題內容進行精準出題。</small>
        </div>
      </div>
    </section>

    <section class="unit-breakdown">
      <h3>📊 各單元掌握程度排行</h3>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>單元名稱</th>
              <th>測驗次數</th>
              <th>平均分數</th>
              <th>教學建議</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in analysis.unit_stats" :key="item.unit">
              <td>{{ item.unit }}</td>
              <td>{{ item.count }}</td>
              <td :class="getScoreClass(item.avg)">{{ item.avg }}%</td>
              <td>
                <span :class="['status-badge', getLevelClass(item.level)]">{{ item.level }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const currentSubject = ref('社會');
const userId = parseInt(localStorage.getItem('user_id'));
const quizResult = ref('');
const generating = ref(false);

const today = new Date().toISOString().split('T')[0];
const lastMonth = new Date();
lastMonth.setMonth(lastMonth.getMonth() - 1);
const lastMonthStr = lastMonth.toISOString().split('T')[0];

const filters = reactive({
  start: lastMonthStr,
  end: today
});

const analysis = ref({
  summary: { total_count: 0, avg_score: 0, failed_count: 0 },
  unit_stats: [],
  concept_map: {}
});

// 💡 計算屬性：從 unit_stats 中過濾出分數較低的單元 (例如低於 90 分)
const weakUnits = computed(() => {
  return (analysis.value.unit_stats || [])
    .filter(item => item.avg < 90)
    .sort((a, b) => a.avg - b.avg); // 分數最低的排在前面
});

watch(currentSubject, () => {
  quizResult.value = ''; 
});

const fetchAnalysis = async () => {
  if (!userId) {
    ElMessage.error("請先登入");
    return;
  }
  try {
    const res = await axios.get('http://localhost:5000/api/teacher/analysis', {
      params: { 
        subject: currentSubject.value, 
        start: filters.start, 
        end: filters.end,
        user_id: userId
      }
    });
    analysis.value = res.data;
  } catch (err) {
    console.error("看板數據讀取失敗:", err);
  }
};

const generateAIQuiz = async () => {
  generating.value = true;
  quizResult.value = ""; 
  try {
    const res = await axios.post('http://localhost:5000/api/teacher/generate_quiz', {
      subject: currentSubject.value,
      user_id: userId 
    });
    
    if (res.data.quiz_content) {
      quizResult.value = res.data.quiz_content;
      ElMessage.success("AI 考卷生成成功！");
    } else {
      ElMessage.warning(res.data.error || "無法生成考卷");
    }
  } catch (err) {
    ElMessage.error("生成失敗，請檢查後端連線。");
  } finally {
    generating.value = false;
  }
};

const copyToClipboard = () => {
  navigator.clipboard.writeText(quizResult.value);
  ElMessage.success("已複製到剪貼簿");
};

const getScoreClass = (score) => {
  if (score < 85) return 'text-danger';
  if (score < 95) return 'text-warn';
  return 'text-success';
};

const getLevelClass = (level) => {
  if (level === '不清楚') return 'bg-danger';
  if (level === '尚可') return 'bg-warn';
  return 'bg-success';
};

onMounted(fetchAnalysis);
</script>

<style scoped>
.teacher-dashboard { margin: 0 auto; padding: 20px; background: #f8f9fa; min-height: 100vh; }
.admin-header { margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }
.filter-controls { display: flex; flex-direction: column; gap: 10px; align-items: flex-end; }
.date-group { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #495057; }
.date-group input { padding: 6px 10px; border: 1px solid #ced4da; border-radius: 6px; outline: none; }

.overview-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
.stat-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 6px solid #339af0; }
.stat-card.warning { border-left-color: #fa5252; }
.stat-card .value { font-size: 28px; font-weight: bold; margin: 10px 0; }
.stat-card .trend { font-size: 13px; color: #868e96; }

/* 🔴 弱點清單樣式優化 */
.concept-analysis { background: white; padding: 20px; border-radius: 12px; margin-bottom: 25px; border: 1px solid #ffd8d8; }
.weak-list { display: flex; flex-direction: column; gap: 12px; margin-top: 15px; }
.weak-item { padding: 15px; background: #fff5f5; border-radius: 8px; border-left: 4px solid #ff6b6b; }
.weak-info { display: flex; justify-content: space-between; margin-bottom: 5px; }
.weak-unit { font-weight: bold; color: #c92a2a; font-size: 16px; }
.weak-count { font-size: 12px; color: #fa5252; background: white; padding: 2px 8px; border-radius: 10px; border: 1px solid #ffc9c9; }
.weak-advice { font-size: 14px; color: #495057; }

.empty-state { color: #adb5bd; font-style: italic; padding: 10px 0; }

.ai-btn {
  width: 100%; padding: 16px;
  background: linear-gradient(135deg, #6610f2 0%, #339af0 100%);
  color: white; border: none; border-radius: 12px; font-size: 17px; font-weight: bold;
  cursor: pointer; margin-bottom: 20px; transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(51, 154, 240, 0.3);
}
.ai-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(51, 154, 240, 0.4); }
.ai-btn:disabled { background: #adb5bd; cursor: not-allowed; box-shadow: none; }

.quiz-display-card { background: #fff; border: 2px solid #339af0; border-radius: 12px; padding: 20px; margin-bottom: 25px; }
.quiz-header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; color: #339af0; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.close-btn { background: #eee; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; }
.quiz-body { white-space: pre-wrap; line-height: 1.6; color: #333; max-height: 500px; overflow-y: auto; font-size: 15px; background: #fafafa; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px inset #eee; }
.quiz-footer { display: flex; justify-content: space-between; align-items: center; }

.unit-breakdown { background: white; padding: 20px; border-radius: 12px; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; padding: 12px; border-bottom: 2px solid #eee; color: #868e96; }
td { padding: 12px; border-bottom: 1px solid #f1f3f5; }

.text-danger { color: #fa5252; font-weight: bold; }
.text-warn { color: #fd7e14; font-weight: bold; }
.text-success { color: #40c057; font-weight: bold; }
.status-badge { padding: 4px 8px; border-radius: 4px; color: white; font-size: 12px; }
.bg-danger { background: #fa5252; }
.bg-warn { background: #fab005; }
.bg-success { background: #40c057; }


</style>