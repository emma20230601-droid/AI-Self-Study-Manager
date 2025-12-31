<template>
  <div class="analysis-container">
    <el-card class="main-card">
      <template #header>
        <div class="header-content">
          <div class="title-group">
            <h2 class="main-title">📈 核心五科學力診斷報告</h2>
            <div class="sub-hint">智慧分析系統：{{ examTitle }}階段</div>
          </div>
          <div class="action-group">
            <el-radio-group v-model="selectedExam" size="default" @change="handleExamChange" class="mr-15">
              <el-radio-button value="all">全學期</el-radio-button>
              <el-radio-button value="midterm">期中</el-radio-button>
              <el-radio-button value="final">期末</el-radio-button>
            </el-radio-group>
            <el-button type="primary" plain :icon="Download" @click="exportToPDF">匯出 PDF 報告</el-button>
          </div>
        </div>
      </template>

      <div id="pdf-content" class="report-wrapper">
        <el-row :gutter="30">
          <el-col :span="9">
            <div class="radar-section">
              <div class="section-label">核心戰力分布</div>
              <div ref="radarChartRef" style="height: 320px;"></div>
            </div>
          </el-col>
          <el-col :span="15">
            <div class="diagnosis-grid">
              <div class="diag-item green">
                <div class="diag-title"><el-icon><CircleCheckFilled /></el-icon> 強勢學科</div>
                <div class="diag-text">{{ strengthAnalysis }}</div>
              </div>
              <div class="diag-item orange">
                <div class="diag-title"><el-icon><WarningFilled /></el-icon> 弱項警示</div>
                <div class="diag-text">{{ weakAnalysis }}</div>
              </div>
              <div class="diag-item blue">
                <div class="diag-title"><el-icon><Promotion /></el-icon> 學習處方</div>
                <div class="diag-text">{{ learningAdvice }}</div>
              </div>
            </div>
          </el-col>
        </el-row>

        <div class="table-container mt-30">
          <div class="section-label">📊 {{ examTitle }}成績匯總統計</div>
          
          <el-table :data="scoreTableWithSum" class="styled-table">
            <el-table-column prop="subject" label="科目" width="100" align="center" fixed>
              <template #default="scope">
                <span class="subject-tag">{{ scope.row.subject }}</span>
              </template>
            </el-table-column>
            
            <template v-if="selectedExam === 'all'">
              <el-table-column prop="dailyAvg" label="平時總均" align="center" />
              <el-table-column prop="reviewScore" label="複習考" align="center" />
              <el-table-column prop="midtermScore" label="期中成績" align="center" />
              <el-table-column prop="finalScore" label="期末成績" align="center" />
            </template>

            <template v-else>
              <el-table-column prop="dailyAvg" label="平時平均" align="center" />
              <el-table-column prop="reviewScore" label="複習考" align="center" />
              <el-table-column prop="examScore" label="定期評量" align="center" class-name="col-highlight" />
            </template>

            <el-table-column label="學期加權" width="130" align="center" fixed="right">
              <template #default="scope">
                <div v-if="scope.row.totalAvg !== '-'" class="final-score-pill" :class="getScorePillClass(scope.row.totalAvg)">
                  {{ scope.row.totalAvg }}
                </div>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <el-divider />

      <div class="section-header"><span class="dot"></span> 單元掌握進度：{{ activeAnalysisSubject }}</div>
      <el-tabs v-model="activeAnalysisSubject" type="border-card" class="mt-15">
        <el-tab-pane v-for="sub in subjects" :key="sub" :label="sub" :name="sub">
          <el-row :gutter="20">
            <el-col :span="13">
              <div :id="'trend-chart-' + sub" class="trend-chart"></div>
            </el-col>
            <el-col :span="11">
              <div class="unit-scroll-list">
                <div v-for="unit in unitData" :key="unit.name" class="unit-item">
                  <div class="unit-info">
                    <span class="u-name">{{ unit.name }}</span>
                    <span class="u-score" :class="getScoreTextColor(unit.avgScore)">
                      {{ unit.avgScore > 0 ? unit.avgScore + '分' : '無成績' }}
                    </span>
                  </div>
                  <el-progress :percentage="unit.progress" :color="customProgressColors" :stroke-width="10" />
                  <div class="u-meta">目標日期：{{ unit.date }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import dayjs from 'dayjs'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import { Download, CircleCheckFilled, WarningFilled, Promotion } from '@element-plus/icons-vue'
import { ElLoading, ElMessage } from 'element-plus'

const userId = parseInt(localStorage.getItem('user_id'))
const progressList = ref([])
const subjects = ['國語', '英文', '數學', '社會', '自然']
const selectedExam = ref('all')
const activeAnalysisSubject = ref('國語')
const radarChartRef = ref(null)
let radarChart = null

// --- 資料過濾 ---
const filteredTasks = computed(() => {
  const mDateStr = localStorage.getItem('midterm_date')
  const midBoundary = mDateStr ? dayjs(mDateStr).format('YYYY-MM-DD') : null

  return progressList.value.filter(t => {
    if (!subjects.includes(t.subject)) return false
    if (!t.target_date) return false
    const taskDate = dayjs(t.target_date).format('YYYY-MM-DD')
    
    if (selectedExam.value === 'midterm') return taskDate <= midBoundary
    if (selectedExam.value === 'final') return taskDate > midBoundary
    return true
  })
})

// --- 核心：表格數據計算 ---
const scoreTable = computed(() => {
  const mDateStr = localStorage.getItem('midterm_date')
  const midBoundary = mDateStr ? dayjs(mDateStr).format('YYYY-MM-DD') : null

  return subjects.map(sub => {
    const subTasks = filteredTasks.value.filter(t => t.subject === sub)
    
    // 平時成績
    const dailyScores = subTasks.filter(t => t.type !== '學校定期評量' && t.score > 0).map(t => Number(t.score))
    const dailyAvg = dailyScores.length ? (dailyScores.reduce((a,b)=>a+b)/dailyScores.length).toFixed(1) : '-'

    // 複習考
    const reviewScore = subTasks.find(t => t.type === '學校定期評量' && t.unit.includes('複習') && t.score > 0)?.score || '-'

    // 定期成績 (分開期中與期末)
    const midtermTask = subTasks.find(t => t.type === '學校定期評量' && !t.unit.includes('複習') && dayjs(t.target_date).format('YYYY-MM-DD') <= midBoundary)
    const finalTask = subTasks.find(t => t.type === '學校定期評量' && !t.unit.includes('複習') && dayjs(t.target_date).format('YYYY-MM-DD') > midBoundary)
    
    const midtermScore = midtermTask?.score || '-'
    const finalScore = finalTask?.score || '-'

    // 當前顯示區段的「段考」成績
    let examScore = '-'
    if (selectedExam.value === 'midterm') examScore = midtermScore
    else if (selectedExam.value === 'final') examScore = finalScore
    else {
        // 全學期時的段考均分
        const examItems = [midtermScore, finalScore].filter(v => v !== '-')
        examScore = examItems.length ? (examItems.reduce((a,b)=>Number(a)+Number(b))/examItems.length).toFixed(1) : '-'
    }

    // 加權總分 (平時 50% + 考試 50%)
    let totalAvg = '-'
    const examPart = [reviewScore, examScore].filter(v => v !== '-')
    const examAvg = examPart.length ? (examPart.reduce((a,b)=>Number(a)+Number(b))/examPart.length) : null

    if (dailyAvg !== '-' && examAvg !== null) {
      totalAvg = (Number(dailyAvg) * 0.5 + examAvg * 0.5).toFixed(1)
    } else if (dailyAvg !== '-') totalAvg = dailyAvg
    else if (examAvg !== null) totalAvg = examAvg.toFixed(1)

    return { 
      subject: sub, 
      dailyAvg, 
      reviewScore, 
      midtermScore, 
      finalScore, 
      examScore, // 這是給區段視圖用的
      totalAvg 
    }
  })
})

const scoreTableWithSum = computed(() => {
  const list = [...scoreTable.value]
  const valid = list.filter(i => i.totalAvg !== '-')
  const avg = valid.length ? (valid.reduce((s,i)=>s+Number(i.totalAvg),0)/valid.length).toFixed(1) : '-'
  list.push({ subject: '總計', dailyAvg: '-', reviewScore: '-', midtermScore: '-', finalScore: '-', examScore: '-', totalAvg: avg })
  return list
})

// --- 診斷與圖表 (同前) ---
const strengthAnalysis = computed(() => {
  const valid = scoreTable.value.filter(i => i.totalAvg !== '-').sort((a,b) => b.totalAvg - a.totalAvg)
  return valid.length ? `${valid[0].subject} 目前為最強勢學科（${valid[0].totalAvg}分）。` : "尚無資料"
})

const weakAnalysis = computed(() => {
  const valid = scoreTable.value.filter(i => i.totalAvg !== '-').sort((a,b) => a.totalAvg - b.totalAvg)
  return valid.length ? `${valid[0].subject} 目前得分較低（${valid[0].totalAvg}分），需加強。` : "尚無資料"
})

const learningAdvice = computed(() => `建議針對 ${activeAnalysisSubject.value} 的弱點單元進行加強複習。`)

const renderRadar = () => {
  if (!radarChartRef.value) return
  radarChart = radarChart || echarts.init(radarChartRef.value)
  const data = scoreTable.value.map(s => s.totalAvg === '-' ? 0 : Number(s.totalAvg))
  radarChart.setOption({
    radar: { indicator: subjects.map(s => ({ name: s, max: 100 })), shape: 'circle' },
    series: [{ type: 'radar', data: [{ value: data, areaStyle: { color: 'rgba(64,158,255,0.2)' } }] }]
  }, true)
}

const renderTrend = () => {
  const sub = activeAnalysisSubject.value
  nextTick(() => {
    const dom = document.getElementById('trend-chart-' + sub)
    if (!dom) return
    let chart = echarts.getInstanceByDom(dom) || echarts.init(dom)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: unitData.value.map(u => u.name), axisLabel: { rotate: 20 } },
      yAxis: { type: 'value', max: 100 },
      series: [{ data: unitData.value.map(u => u.avgScore), type: 'line', smooth: true }]
    }, true)
  })
}

const exportToPDF = async () => {
  const loading = ElLoading.service({ text: '報告生成中...' });
  const element = document.getElementById('pdf-content');
  const canvas = await html2canvas(element, { scale: 2 });
  const pdf = new jsPDF('p', 'mm', 'a4');
  pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 10, 210, (canvas.height * 210) / canvas.width);
  pdf.save(`${examTitle.value}_報告.pdf`);
  loading.close();
}

const unitData = computed(() => {
  const subTasks = filteredTasks.value.filter(t => t.subject === activeAnalysisSubject.value)
  const units = {}
  subTasks.forEach(t => {
    const name = t.unit || '基礎內容'
    if (!units[name]) units[name] = { name, scores: [], progress: [], date: t.target_date }
    if (t.score > 0) units[name].scores.push(Number(t.score))
    units[name].progress.push(Number(t.progress_percent || 0))
  })
  return Object.values(units).map(u => ({
    name: u.name,
    avgScore: u.scores.length ? Math.round(u.scores.reduce((a,b)=>a+b)/u.scores.length) : 0,
    progress: u.progress.length ? Math.round(u.progress.reduce((a,b)=>a+b)/u.progress.length) : 0,
    date: u.date
  })).sort((a,b) => dayjs(a.date).diff(dayjs(b.date)))
})

const getScorePillClass = (s) => (s < 60) ? 'bg-red' : (s < 90 ? 'bg-orange' : 'bg-green')
const getScoreTextColor = (s) => (s < 60) ? 'c-red' : (s < 90 ? 'c-orange' : 'c-green')
const examTitle = computed(() => selectedExam.value === 'midterm' ? '期中' : (selectedExam.value === 'final' ? '期末' : '全學期'))
const handleExamChange = () => { nextTick(() => { renderRadar(); renderTrend(); }) }

onMounted(async () => {
  const res = await axios.get(`http://localhost:5000/progress/with_tasks?user_id=${userId}`)
  progressList.value = res.data
  handleExamChange()
})
watch(activeAnalysisSubject, renderTrend)
const customProgressColors = [{ color: '#f56c6c', percentage: 40 }, { color: '#e6a23c', percentage: 70 }, { color: '#67c23a', percentage: 100 }]
</script>

<style scoped>
.analysis-container { padding: 30px; background-color: #f4f7f9; min-height: 100vh; }
.main-card { border-radius: 16px; border: none; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.header-content { display: flex; justify-content: space-between; align-items: center; }
.main-title { margin: 0; font-size: 1.6rem; }
.diagnosis-grid { display: flex; flex-direction: column; gap: 15px; }
.diag-item { padding: 18px; border-radius: 12px; }
.green { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
.orange { background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; }
.blue { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; }
.styled-table { border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }
.subject-tag { background: #f1f5f9; padding: 4px 12px; border-radius: 6px; font-weight: bold; }
.final-score-pill { display: inline-block; width: 75px; height: 34px; line-height: 34px; border-radius: 17px; font-weight: 800; color: white; text-align: center;}
.bg-green { background-color: #10b981; }
.bg-orange { background-color: #f59e0b; }
.bg-red { background-color: #ef4444; }
.section-label { font-size: 1.1rem; font-weight: bold; margin-bottom: 15px; display: flex; align-items: center; }
.section-label::before { content: ""; width: 4px; height: 18px; background: #3b82f6; margin-right: 10px; border-radius: 2px; }
.mt-30 { margin-top: 30px; }
.mr-15 { margin-right: 15px; }
.trend-chart { height: 320px; width: 100%; }
.unit-scroll-list { max-height: 320px; overflow-y: auto; }
.unit-item { background: #fff; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #e2e8f0; }
</style>