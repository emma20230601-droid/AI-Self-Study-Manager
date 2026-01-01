<template>
  <div class="task-list-page">
    <el-card class="list-card" shadow="never">
      <div class="header-section">
        <div class="title-info">
          <h2>📋 學習進度總表</h2>
          <span class="sub-hint">精確管控每一單元的執行細節與完成狀態</span>
        </div>
        
        <div class="filter-controls">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="開始日期"
            end-placeholder="結束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="range-picker"
            @change="handleFilterChange"
          />
          <el-select v-model="selectedSubject" placeholder="篩選科目" clearable style="width: 140px; margin-left: 10px;">
            <el-option label="🌟 全部顯示" value="" />
            <el-option v-for="s in subjectOrder" :key="s" :label="s" :value="s" />
          </el-select>
        </div>
      </div>

      <el-form :model="taskForm" class="add-task-form" @submit.prevent="addTask">
        <el-row :gutter="10">
          <el-col :span="3">
            <el-select v-model="taskForm.subject" placeholder="科目">
              <el-option v-for="s in subjectOrderFull" :key="s" :label="s" :value="s" />
            </el-select>
          </el-col>
          <el-col :span="3">
            <el-select v-model="taskForm.type" placeholder="類型">
              <el-option v-for="t in typeOrder" :key="t" :label="t" :value="t" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-input v-model="taskForm.unit" placeholder="單元名稱 (分析核心)" />
          </el-col>
          <el-col :span="7">
            <el-input v-model="taskForm.title" placeholder="詳細內容 (頁碼、範圍...)" />
          </el-col>
          <el-col :span="4">
            <el-date-picker v-model="taskForm.date" type="date" placeholder="日期" style="width: 100%" />
          </el-col>
          <el-col :span="2">
            <el-button type="primary" @click="addTask" class="w-100">新增</el-button>
          </el-col>
        </el-row>
      </el-form>

      <el-table 
        :data="filteredTasks" 
        style="margin-top: 20px" 
        border 
        stripe
        row-class-name="task-row"
      >
        <el-table-column label="執行日期" width="130" align="center">
          <template #default="scope">
            <span class="date-display">{{ formatDate(scope.row.date) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="分類項目" width="180">
          <template #default="scope">
            <div class="category-wrapper">
              <span :class="['subject-dot', getSubjectColorClass(scope.row.subject)]"></span>
              <span class="subject-name">{{ scope.row.subject }}</span>
              <span class="type-badge">{{ scope.row.type }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="單元名稱" min-width="180">
          <template #default="scope">
            <div class="unit-text">{{ scope.row.unit }}</div>
          </template>
        </el-table-column>

        <el-table-column label="內容詳情" prop="title" min-width="250" show-overflow-tooltip />

        <el-table-column label="進度狀態" width="160" align="center">
          <template #default="scope">
            <el-select 
              v-model="scope.row.status" 
              @change="updateStatus(scope.row)" 
              size="small" 
              :class="`status-picker-${scope.row.status}`"
            >
              <el-option label="未開始" value="未開始" />
              <el-option label="進行中" value="進行中" />
              <el-option label="已完成" value="已完成" />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column label="管理" width="120" align="center" fixed="right">
          <template #default="scope">
            <el-button :icon="Edit" type="primary" link @click="openEditDialog(scope.row)">編輯</el-button>
            <el-button :icon="Delete" type="danger" link @click="deleteTask(scope.row.id)">刪除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showEditDialog" title="📝 修改學習任務" width="520px" destroy-on-close>
      <el-form :model="editingTask" label-width="100px" v-if="editingTask">
        <el-form-item label="科目/類型">
          <div style="display: flex; gap: 10px; width: 100%;">
            <el-select v-model="editingTask.subject" style="flex: 1">
              <el-option v-for="s in subjectOrderFull" :key="s" :label="s" :value="s" />
            </el-select>
            <el-select v-model="editingTask.type" style="flex: 1">
              <el-option v-for="t in typeOrder" :key="t" :label="t" :value="t" />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="單元名稱">
          <el-input v-model="editingTask.unit" placeholder="例如：第一章 分數的運算" />
        </el-form-item>
        <el-form-item label="詳細內容">
          <el-input v-model="editingTask.title" type="textarea" :rows="3" placeholder="具體練習內容..." />
        </el-form-item>
        <el-form-item label="執行日期">
          <el-date-picker v-model="editingTask.date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="當前狀態">
          <el-radio-group v-model="editingTask.status">
            <el-radio value="未開始">未開始</el-radio>
            <el-radio value="進行中">進行中</el-radio>
            <el-radio value="已完成">已完成</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateTask">確認儲存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

// 1. 定義 API 基礎網址
const API_BASE = import.meta.env.VITE_API_BASE_URL
const userId = parseInt(localStorage.getItem('user_id'))

// 篩選控制
const dateRange = ref([]) 
const selectedSubject = ref('')
const taskList = ref([])

// 表單相關
const taskForm = ref({ subject: '國語', type: '自修', unit: '', title: '', date: new Date() })
const editingTask = ref(null)
const showEditDialog = ref(false)

// 常數清單
const subjectOrder = ['國語', '數學', '英文', '社會', '自然', '生物', '理化']
const subjectOrderFull = [...subjectOrder, '藝術', '其它']
const typeOrder = ['自修', '評量', '學校課本', '學校作業', '考卷', '小科', '加深加廣', '戶外活動', '考試', '報名']

// --- API 函式區 ---

const fetchTasks = async () => {
  if (!userId) return
  try {
    // 修正路徑：localhost -> API_BASE
    const res = await axios.get(`${API_BASE}/tasks`, {
      params: { user_id: userId }
    })
    taskList.value = res.data
    sortTasks()
  } catch (err) {
    console.error('載入失敗:', err)
    ElMessage.error('任務載入失敗，請檢查後端狀態')
  }
}

const addTask = async () => {
  if (!taskForm.value.unit || !taskForm.value.title) return ElMessage.warning('請輸入單元與內容')
  try {
    const payload = { 
      ...taskForm.value, 
      user_id: userId, 
      date: dayjs(taskForm.value.date).format('YYYY-MM-DD'), 
      status: '未開始' 
    }
    // 修正路徑
    const res = await axios.post(`${API_BASE}/tasks`, payload)
    taskList.value.unshift(res.data)
    taskForm.value = { subject: '國語', type: '自修', unit: '', title: '', date: new Date() }
    ElMessage.success('任務已新增')
  } catch (err) { 
    ElMessage.error('新增失敗') 
  }
}

const updateStatus = async (task) => {
  try {
    // 修正路徑
    await axios.patch(`${API_BASE}/tasks/${task.id}`, { 
      status: task.status, 
      user_id: userId 
    })
    ElMessage.success(`進度更新：${task.status}`)
  } catch (err) { 
    ElMessage.error('更新失敗') 
  }
}

const updateTask = async () => {
  try {
    // 修正路徑
    const res = await axios.patch(`${API_BASE}/tasks/${editingTask.value.id}`, { 
      ...editingTask.value, 
      user_id: userId 
    })
    const idx = taskList.value.findIndex(t => t.id === editingTask.value.id)
    if (idx !== -1) taskList.value[idx] = res.data
    showEditDialog.value = false
    ElMessage.success('修改已儲存')
  } catch (err) { 
    ElMessage.error('儲存失敗') 
  }
}

const deleteTask = async (id) => {
  try {
    await ElMessageBox.confirm('確定要永久刪除此任務嗎？', '提醒', {
      confirmButtonText: '確定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    // 修正路徑
    await axios.delete(`${API_BASE}/tasks/${id}`, { 
      params: { user_id: userId } 
    })
    taskList.value = taskList.value.filter(t => t.id !== id)
    ElMessage.success('已刪除任務')
  } catch (err) {
    // 使用者取消刪除不噴錯
  }
}

// --- 輔助函式區 ---

const filteredTasks = computed(() => {
  return taskList.value.filter(task => {
    const matchSubject = !selectedSubject.value || task.subject === selectedSubject.value
    let matchDate = true
    if (dateRange.value && dateRange.value.length === 2) {
      const start = dayjs(dateRange.value[0]).startOf('day')
      const end = dayjs(dateRange.value[1]).endOf('day')
      const taskDate = dayjs(task.date)
      matchDate = (taskDate.isAfter(start) || taskDate.isSame(start)) && 
                  (taskDate.isBefore(end) || taskDate.isSame(end))
    }
    return matchSubject && matchDate
  })
})

const sortTasks = () => {
  taskList.value.sort((a, b) => new Date(b.date) - new Date(a.date))
}

const openEditDialog = (row) => { 
  editingTask.value = { ...row }
  showEditDialog.value = true 
}

const getSubjectColorClass = (s) => {
  const map = { '國語': 'bg-red', '數學': 'bg-blue', '英文': 'bg-purple', '自然': 'bg-green', '社會': 'bg-orange' }
  return map[s] || 'bg-gray'
}

const formatDate = (d) => d ? dayjs(d).format('YYYY-MM-DD') : '--'

onMounted(fetchTasks)
</script>

<style scoped>
.task-list-page { padding: 24px; background: #f0f2f5; min-height: 100vh; }
.list-card { border-radius: 12px; border: none; box-shadow: 0 4px 16px rgba(0,0,0,0.05); }

.header-section { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.title-info h2 { margin: 0; font-size: 1.6rem; color: #1f2f3d; font-weight: bold; }
.sub-hint { font-size: 14px; color: #909399; margin-top: 4px; display: block; }

.add-task-form { background: #fafafa; padding: 20px; border-radius: 10px; border: 1px dashed #dcdfe6; margin-bottom: 25px; }

/* 科目與類型視覺優化 */
.category-wrapper { display: flex; align-items: center; gap: 10px; }
.subject-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.subject-name { font-weight: 600; color: #303133; min-width: 45px; }
.type-badge { background: #f0f2f5; color: #606266; font-size: 11px; padding: 2px 10px; border-radius: 12px; border: 1px solid #dcdfe6; white-space: nowrap; }

/* 科目顏色定義 */
.bg-red { background: #f56c6c; box-shadow: 0 0 4px #f56c6c; }
.bg-blue { background: #409eff; box-shadow: 0 0 4px #409eff; }
.bg-purple { background: #9c27b0; box-shadow: 0 0 4px #9c27b0; }
.bg-green { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.bg-orange { background: #e6a23c; box-shadow: 0 0 4px #e6a23c; }
.bg-gray { background: #909399; }

.date-display { font-family: 'SFMono-Regular', Consolas, monospace; font-weight: bold; color: #444; }
.unit-text { color: #409eff; font-weight: 700; font-size: 15px; }

/* 狀態選擇器顏色 */
.status-picker-已完成 :deep(.el-input__inner) { color: #67c23a !important; font-weight: 900; }
.status-picker-進行中 :deep(.el-input__inner) { color: #e6a23c !important; font-weight: 900; }
.status-picker-未開始 :deep(.el-input__inner) { color: #909399 !important; }

.w-100 { width: 100%; }

/* 🏆 讓表格整體變圓的核心設定 */
:deep(.el-table) {
  border-radius: 20px !important; /* 調整這裡的數值來決定圓度 */
  overflow: hidden !important;    /* 這是關鍵：剪裁內部的直角儲存格 */
  border: 1px solid #ebeef5;      /* 加上淡淡邊框讓圓角更明顯 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.03); /* 增加一點點陰影感 */
}

/* 讓表格頂部標頭也配合圓角 */
:deep(.el-table th.el-table__cell) {
  background-color: #f5f7fa !important; 
  color: #333;
  font-weight: 800;
  border-bottom: none !important;
}

/* 移除最後一行底部的線，避免破壞圓角美感 */
:deep(.el-table__inner-wrapper::before) {
  display: none;
}

</style>
