<template>
  <div class="full-page-container">
    <el-card class="main-card-full">
      <div class="page-header">
        <div class="title-wrap">
          <h2>📘 學習成就軌跡看板</h2>
          <div class="header-hint">記錄分數、掌握進度、複盤心得，見證成長的每一刻</div>
        </div>
        
        <div class="filter-section">
          <el-date-picker
            v-model="selectedMonth"
            type="month"
            placeholder="選擇月份"
            size="large"
            format="YYYY 年 MM 月"
            value-format="YYYY-MM"
            style="width: 200px"
          />
          <el-select 
            v-model="selectedSubject" 
            placeholder="選擇科目" 
            clearable 
            size="large" 
            style="width: 140px"
          >
            <el-option v-for="item in subjectOrder" :key="item" :label="item" :value="item" />
          </el-select>
          <el-button @click="clearFilter" size="large" round>清除篩選</el-button>
        </div>
      </div>

      <el-table
        ref="progressTable"
        :data="filteredAndSortedList"
        stripe
        border
        height="calc(100vh - 260px)" 
        class="custom-table"
        :row-class-name="tableRowClassName"
      >
        <el-table-column label="科目" prop="subject" width="110" align="center">
          <template #default="scope">
            <span class="subject-tag">{{ scope.row.subject }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="類型" prop="type" width="110" align="center" />
        <el-table-column label="單元" prop="unit" width="140" />
        <el-table-column label="內容" prop="title" min-width="180" />
        
        <el-table-column label="📅 目標日期" width="140" align="center">
          <template #default="scope">
            {{ formatDate(scope.row.target_date) }}
          </template>
        </el-table-column>

        <el-table-column label="⏳ 倒數" width="110" align="center">
          <template #default="scope">
            <span v-if="scope.row.progress_percent === 100" class="status-done">已完成</span>
            <span v-else :class="{'status-urgent': scope.row.daysLeft < 0}">
              {{ scope.row.daysLeft < 0 ? '逾期 ' + Math.abs(scope.row.daysLeft) : scope.row.daysLeft }} 天
            </span>
          </template>
        </el-table-column>

        <el-table-column label="📈 執行進度" width="280">
          <template #default="scope">
            <el-slider
              v-model="scope.row.progress_percent"
              :step="10"
              show-input
              class="custom-slider"
              :class="scope.row.progress_percent < 100 ? 'slider-not-finished' : 'slider-finished'"
            />
          </template>
        </el-table-column>

        <el-table-column label="💯 分數" width="110">
          <template #default="scope">
            <el-input
              type="textarea"
              v-model="scope.row.score"
              placeholder="必填"
              autosize
              class="large-input score-input"
              :class="{ 'is-empty': !scope.row.score || String(scope.row.score).trim() === '' }"
            />
          </template>
        </el-table-column>

        <el-table-column label="💭 學習筆記/錯題心得" min-width="250">
          <template #default="scope">
            <div class="note-cell">
              <el-input
                type="textarea"
                v-model="scope.row.student_note"
                placeholder="點擊輸入心得..."
                autosize
                class="large-input"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="110" fixed="right" align="center">
          <template #default="scope">
            <el-button type="primary" size="large" @click="saveProgress(scope.row)" round>儲存</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const progressTable = ref(null)
const selectedMonth = ref(dayjs().format('YYYY-MM'))
const selectedSubject = ref(null)
const userId = parseInt(localStorage.getItem('user_id'))
const progressList = ref([])

const subjectOrder = ['國語', '數學', '英文', '社會', '自然', '其它']
const API_BASE = import.meta.env.VITE_API_BASE_URL;

const fetchProgress = async () => {
  try {
    // 修正路徑使用樣板字串
    const res = await axios.get(`${API_BASE}/progress/with_tasks?user_id=${userId}`)
    progressList.value = res.data.map(item => {
      const isCompleted = Number(item.progress_percent) === 100 || item.status === '已完成'
      return {
        ...item,
        progress_percent: isCompleted ? 100 : (item.progress_percent || 0),
        daysLeft: getDaysLeft(item.target_date, isCompleted),
      }
    })
  } catch (err) { console.error('API Error:', err) }
}

const filteredAndSortedList = computed(() => {
  let list = progressList.value
  if (selectedMonth.value) list = list.filter(i => dayjs(i.target_date).format('YYYY-MM') === selectedMonth.value)
  if (selectedSubject.value) list = list.filter(i => i.subject === selectedSubject.value)
  return [...list].sort((a, b) => {
    const dateDiff = dayjs(a.target_date).diff(dayjs(b.target_date))
    if (dateDiff !== 0) return dateDiff
    return subjectOrder.indexOf(a.subject) - subjectOrder.indexOf(b.subject)
  })
})

const tableRowClassName = ({ row }) => {
  return dayjs(row.target_date).format('YYYY-MM-DD') === dayjs().format('YYYY-MM-DD') ? 'row-today' : ''
}

const saveProgress = async (row) => {
  if (row.score === null || row.score === undefined || String(row.score).trim() === '') {
    ElMessage.warning({
      message: `請填寫「${row.subject}」的分數後再儲存`,
      showClose: true,
      duration: 3000
    })
    return 
  }

  try {
    const payload = { 
      task_id: row.task_id, 
      progress_percent: row.progress_percent, 
      student_note: row.student_note, 
      score: row.score, 
      date: dayjs().format('YYYY-MM-DD'), 
      user_id: userId 
    }
    
    if (row.id) {
      await axios.patch(`${API_BASE}/progress/${row.id}`, payload)
    } else {
      const res = await axios.post(`${API_BASE}/progress`, payload) 
      row.id = res.data.id
    }
    
    if (row.progress_percent === 100) {
      await axios.patch(`${API_BASE}/tasks/${row.task_id}`, { status: '已完成', user_id: userId })
    }
    
    ElMessage.success('學習進度已成功記錄！')
  } catch (err) { 
    console.error(err)
    ElMessage.error('儲存失敗，請檢查網絡連線') 
  }
}

const getDaysLeft = (targetDate, isCompleted) => isCompleted ? 0 : dayjs(targetDate).startOf('day').diff(dayjs().startOf('day'), 'day')
const formatDate = (dateStr) => dayjs(dateStr).format('YYYY-MM-DD')
const clearFilter = () => { selectedMonth.value = null; selectedSubject.value = null }

onMounted(async () => {
  await fetchProgress()
})
</script>

<style scoped>
.full-page-container {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  min-height: calc(100vh - 60px);
}

.main-card-full {
  border-radius: 24px;
  border: none;
  height: calc(100vh - 100px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.08);
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 10px 20px 10px;
}

h2 { font-size: 2.2rem; font-weight: 900; color: #1a1a1a; margin: 0; }
.header-hint { font-size: 1.05rem; color: #7f8c8d; margin-top: 5px; }

:deep(.el-table) { font-size: 1.15rem; border-radius: 16px; overflow: hidden; }
:deep(.el-table th.el-table__cell) { background-color: #f8f9fb !important; color: #2c3e50; font-weight: 800; height: 65px; }

.subject-tag {
  background: #e6f7ff;
  padding: 6px 14px;
  border-radius: 20px;
  color: #1890ff;
  font-weight: 800;
  display: inline-block;
}

.score-input.is-empty :deep(.el-textarea__inner) {
  border: 1px solid #ffbb96 !important;
  background-color: #fff7e6 !important;
}

.status-done { background: #f6ffed; color: #52c41a; padding: 4px 12px; border-radius: 10px; font-weight: bold; }
.status-urgent { background: #fff1f0; color: #ff4d4f; padding: 4px 12px; border-radius: 10px; font-weight: bold; }

.note-cell { display: flex; gap: 10px; align-items: flex-start; }

.large-input :deep(.el-textarea__inner) {
  font-size: 1.1rem;
  padding: 10px;
  border-radius: 12px;
}

.row-today { background-color: #fffdf0 !important; }
.row-today td:first-child { border-left: 8px solid #faad14 !important; }

.el-button { border-radius: 12px; font-weight: 600; }

/* ==========================================================================
   手機版專屬 (只改手機，不動電腦)
   ========================================================================== */
@media (max-width: 768px) {
  /* A. 頁面洗白與固定 */
  .full-page-container {
    padding: 0 !important;
    background: #ffffff !important; /* 強制白底 */
    height: 100vh !important;
    overflow: hidden !important;
    display: flex;
    flex-direction: column;
  }

  .main-card-full {
    height: 100% !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    background: #ffffff !important;
    display: flex;
    flex-direction: column;
  }

  /* B. 標題區縮小 */
  .page-header {
    flex-direction: column;
    padding: 10px 15px !important;
    gap: 10px;
  }
  h2 { font-size: 1.4rem !important; }
  .header-hint { display: none; } /* 手機版隱藏副標題節省空間 */

  /* C. 篩選區寬度自適應 */
  .filter-section {
    width: 100%;
    display: flex;
    gap: 5px;
  }
  .filter-section :deep(.el-date-editor.el-input),
  .filter-section :deep(.el-select) {
    flex: 1 !important;
    width: auto !important;
  }

  /* D. 表格手機版「瘦身」：隱藏次要欄位，防止水平撐破 */
  :deep(.el-table__header-wrapper th:nth-child(2)), /* 類型 */
  :deep(.el-table__body-wrapper td:nth-child(2)),
  :deep(.el-table__header-wrapper th:nth-child(3)), /* 單元 */
  :deep(.el-table__body-wrapper td:nth-child(3)) {
    display: none !important;
  }

  /* E. 讓表格內部可以水平滑動，但外層不動 */
  :deep(.el-table) {
    width: 100% !important;
    font-size: 13px !important;
  }

  /* F. 讓進度條在手機上變短，避免擠壓 */
  .custom-slider {
    width: 120px !important;
  }

  /* G. 調整輸入框高度與字體 */
  :deep(.el-textarea__inner) {
    font-size: 13px !important;
    padding: 5px !important;
  }

  /* H. 鎖定 el-main 防止灰底與晃動 */
  :deep(.el-main) {
    padding: 0 !important;
    background: #ffffff !important;
    overflow-x: hidden !important;
  }
}
</style>