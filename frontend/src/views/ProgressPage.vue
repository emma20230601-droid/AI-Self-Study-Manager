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
            style="width: 140px; margin-left: 10px;"
          >
            <el-option v-for="item in subjectOrder" :key="item" :label="item" :value="item" />
          </el-select>
          <el-button @click="clearFilter" size="large" round style="margin-left: 10px;">清除篩選</el-button>
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

        <el-table-column label="⏳ 狀態/倒數" width="110" align="center">
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
            />
          </template>
        </el-table-column>

        <el-table-column label="💯 分數" width="110">
          <template #default="scope">
            <el-input
              v-model="scope.row.score"
              placeholder="必填"
              class="score-input"
              :class="{ 'is-empty': !scope.row.score && row.score !== 0 }"
            />
          </template>
        </el-table-column>

        <el-table-column label="💭 學習筆記/錯題心得" min-width="250">
          <template #default="scope">
            <el-input
              type="textarea"
              v-model="scope.row.student_note"
              placeholder="輸入心得..."
              autosize
              class="large-input"
            />
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

const selectedMonth = ref(dayjs().format('YYYY-MM'))
const selectedSubject = ref(null)
const userId = parseInt(localStorage.getItem('user_id'))
const progressList = ref([])

const subjectOrder = ['國語', '數學', '英文', '社會', '自然', '理化', '生物', '其它', '藝術', '國中入學考', '小科加課']

// 獲取資料
const fetchProgress = async () => {
  try {
    const res = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/progress/with_tasks`, {
      params: { user_id: userId },
      withCredentials: true
    });
    progressList.value = res.data.map(item => ({
      ...item,
      daysLeft: getDaysLeft(item.target_date, item.progress_percent === 100)
    }))
  } catch (err) { 
    console.error('抓取資料失敗:', err)
    ElMessage.error('無法連線到伺服器')
  }
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
  return dayjs(row.target_date).isSame(dayjs(), 'day') ? 'row-today' : ''
}

// 🚀 儲存功能
const saveProgress = async (row) => {
  // 分數校驗
  if (row.score === null || row.score === undefined || String(row.score).trim() === '') {
    ElMessage.warning(`請填寫「${row.subject}」的分數後再儲存`)
    return
  }

  const payload = { 
    task_id: row.task_id, 
    progress_percent: row.progress_percent, 
    student_note: row.student_note || '', 
    score: row.score, 
    date: dayjs().format('YYYY-MM-DD'), 
    user_id: userId 
  }
  
  try {
    if (row.id) {
      try {
        // 嘗試更新 (PATCH)
        await axios.patch(`${import.meta.env.VITE_API_BASE_URL}/progress/${row.id}`, payload, { withCredentials: true });
      } catch (patchErr) {
        // 如果報 404，代表雲端沒這筆 ID，改走 POST 新增
        if (patchErr.response?.status === 404) {
          const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/progress`, payload, { withCredentials: true });
          row.id = res.data.id;
        } else {
          throw patchErr;
        }
      }
    } else {
      // 直接新增 (POST)
      const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/progress`, payload, { withCredentials: true });
      row.id = res.data.id;
    }
    
    // 如果進度 100%，同步更新 Task 狀態
    if (row.progress_percent === 100) {
      await axios.patch(`${import.meta.env.VITE_API_BASE_URL}/tasks/${row.task_id}`, 
        { status: '已完成', user_id: userId }, 
        { withCredentials: true }
      );
    }
    
    ElMessage.success('儲存成功！')
  } catch (err) { 
    console.error('儲存失敗:', err)
    ElMessage.error('儲存失敗，請確認網路連線') 
  }
}

const getDaysLeft = (targetDate, isCompleted) => isCompleted ? 0 : dayjs(targetDate).startOf('day').diff(dayjs().startOf('day'), 'day')
const formatDate = (dateStr) => dayjs(dateStr).format('YYYY-MM-DD')
const clearFilter = () => { selectedMonth.value = null; selectedSubject.value = null }

onMounted(fetchProgress)
</script>

<style scoped>
.full-page-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.main-card-full {
  border-radius: 20px;
  height: calc(100vh - 100px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.05);
}

.page-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.subject-tag {
  background: #e6f7ff;
  color: #1890ff;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: bold;
}

.status-done { color: #52c41a; font-weight: bold; }
.status-urgent { color: #ff4d4f; font-weight: bold; }

.large-input :deep(.el-textarea__inner) {
  border-radius: 8px;
  padding: 8px;
}

.score-input.is-empty :deep(.el-input__inner) {
  border-color: #ffa39e;
  background-color: #fff1f0;
}

.row-today { background-color: #fffbe6 !important; }
</style>
