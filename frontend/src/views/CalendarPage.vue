<template>
  <div class="calendar-page">
    <el-card class="calendar-card" shadow="never">
      <div class="calendar-controls">
        <div class="title-section">
          <h2>📅 學習成就月曆</h2>
          <span class="sub-title">雙擊日期新增，單擊編輯，拖拽任務可調整日期</span>
        </div>
        
        <div class="action-section">
          <el-button-group>
            <el-button @click="goToPreviousMonth" icon="ArrowLeft">上個月</el-button>
            <el-button class="current-month-display">
              {{ currentMonth.format('YYYY 年 MM 月') }}
            </el-button>
            <el-button @click="goToNextMonth">下個月<el-icon class="el-icon--right"><ArrowRight /></el-icon></el-button>
          </el-button-group>
          <el-button type="success" @click="printCurrent" icon="Printer" plain style="margin-left: 10px">列印本月報表</el-button>
        </div>
      </div>

      <div class="calendar-grid">
        <div v-for="(day, idx) in weekDays" :key="day" class="day-header" :class="{ 'weekend': idx === 0 || idx === 6 }">
          {{ day }}
        </div>

        <div
          v-for="(date, index) in calendarDays"
          :key="index"
          class="calendar-cell"
          :class="{
            'other-month': date.month() !== currentMonth.month(),
            'is-today': isToday(date),
            'drag-over': dragOverDate === formatDate(date)
          }"
          @dragover.prevent
          @dragenter.prevent="dragOverDate = formatDate(date)"
          @dragleave="dragOverDate = null"
          @drop="onDrop(date)"
          @dblclick="openAddDialog(date)"
        >
          <div class="cell-top">
            <span class="date-number">{{ date.date() }}</span>
          </div>
          
          <div class="task-container">
            <div
              v-for="task in tasksByDate[formatDate(date)] || []"
              :key="task.id"
              class="task-item"
              :class="[getSubjectClass(task.subject), { 'is-done': task.status === '已完成' }]"
              draggable="true"
              @dragstart="dragTask = task"
              @click="openEditDialog(task)"
            >
              <span class="status-icon">{{ getStatusIcon(task.status) }}</span>
              <span class="task-content">
                <strong>{{ task.subject }}</strong> ({{ task.type }})：{{ task.title }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="showAddDialog" title="➕ 新增學習任務" width="500px">
      <el-form :model="newTask" label-width="100px">
        <el-form-item label="科目">
          <el-select v-model="newTask.subject" style="width:100%">
            <el-option v-for="s in subjectOrder" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="類型">
          <el-select v-model="newTask.type" style="width:100%">
            <el-option v-for="t in typeOrder" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="單元名稱">
          <el-input 
            v-model="newTask.unit" 
            placeholder="例如：第一單元、分數的乘法、期中考範圍"
          />
        </el-form-item>

        <el-form-item label="詳細內容">
          <el-input 
            v-model="newTask.title" 
            type="textarea" 
            :rows="3" 
            placeholder="請輸入頁碼、講義範圍或是具體的錯題內容..." 
          />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="newTask.date" type="date" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addTask">確認新增</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="📝 編輯學習任務" width="550px" destroy-on-close>
    <el-form :model="editingTask" v-if="editingTask" label-width="100px" label-position="left">
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="科目">
            <el-select v-model="editingTask.subject" style="width:100%">
              <el-option v-for="s in subjectOrder" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="類型">
            <el-select v-model="editingTask.type" style="width:100%">
              <el-option v-for="t in typeOrder" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="單元名稱">
        <el-input 
          v-model="editingTask.unit" 
          placeholder="例如：第一單元、分數的乘法、期中考範圍"
        />
      </el-form-item>

      <el-form-item label="詳細內容">
        <el-input 
          v-model="editingTask.title" 
          type="textarea" 
          :rows="3" 
          placeholder="請輸入頁碼、講義範圍或是具體的錯題內容..." 
        />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="進度狀態">
            <el-select v-model="editingTask.status" style="width:100%">
              <el-option label="☐ 未開始" value="未開始" />
              <el-option label="⏳ 進行中" value="進行中" />
              <el-option label="✅ 已完成" value="已完成" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="調整日期">
            <el-date-picker 
              v-model="editingTask.date" 
              type="date" 
              style="width:100%" 
              format="YYYY-MM-DD" 
              value-format="YYYY-MM-DD" 
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <div style="display:flex; justify-content: space-between">
        <el-button type="danger" @click="deleteTask(editingTask.id)" plain>刪除任務</el-button>
        <div>
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="updateTask">儲存修改</el-button>
        </div>
      </div>
    </template>
  </el-dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, Printer } from '@element-plus/icons-vue'
import { exportMonthCalendarPDF } from "@/utils/exportCalendarPdf";

const userId = parseInt(localStorage.getItem('user_id'))
const currentMonth = ref(dayjs())
const taskList = ref([])
const weekDays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
const formatDate = (d) => dayjs(d).format('YYYY-MM-DD')

const subjectOrder = ['國語', '數學', '英文', '社會', '自然', '理化', '生物', '其它', '藝術', '國中入學考', '小科加課']
const typeOrder = ['自修', '評量', '學校課本', '學校作業', '考卷', '小科', '加深加廣', '戶外活動', '考試', '報名']

const fetchTasks = async () => {
  try {
    const res = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/tasks`, {
      params: { user_id: userId },
      withCredentials: true
    });
    taskList.value = res.data.sort((a, b) => {
      const aSub = subjectOrder.indexOf(a.subject), bSub = subjectOrder.indexOf(b.subject)
      if (aSub !== bSub) return aSub - bSub
      return new Date(a.date) - new Date(b.date)
    })
  } catch (err) { console.error(err) }
}

const tasksByDate = computed(() => {
  const map = {}
  taskList.value.forEach(task => {
    if (!map[task.date]) map[task.date] = []
    map[task.date].push(task)
  })
  return map
})

const calendarDays = computed(() => {
  const start = currentMonth.value.startOf('month').startOf('week')
  const end = currentMonth.value.endOf('month').endOf('week')
  const days = []
  let date = start
  while (date.isBefore(end) || date.isSame(end)) {
    days.push(date)
    date = date.add(1, 'day')
  }
  return days
})

const goToPreviousMonth = () => { currentMonth.value = currentMonth.value.subtract(1, 'month') }
const goToNextMonth = () => { currentMonth.value = currentMonth.value.add(1, 'month') }
const isToday = (date) => dayjs().isSame(date, 'day')

const getStatusIcon = (status) => {
  switch(status){
    case '已完成': return '✅'
    case '進行中': return '⏳'
    default: return '☐'
  }
}

const getSubjectClass = (subject) => {
  const map = { 國語:'chinese', 數學:'math', 社會:'social', 自然:'science', 理化:'physics', 生物:'biology', 英文:'english', 藝術:'art', 國中入學考:'exam', 小科加課:'extra' }
  for (const key in map) if (subject.includes(key)) return map[key]
  return 'default-subject'
}

const showAddDialog = ref(false), showEditDialog = ref(false)
const newTask = ref({ subject: '數學', type: '自修', unit: '', title: '', date: '', status: '未開始' })
const editingTask = ref(null)
const dragTask = ref(null), dragOverDate = ref(null)

const openAddDialog = (date) => {
  newTask.value = { subject: '數學', type: '自修', unit: '', title: '', date: formatDate(date), status: '未開始' }
  showAddDialog.value = true
}

const addTask = async () => {
  try {
    const payload = { ...newTask.value, user_id: userId, date: dayjs(newTask.value.date).format('YYYY-MM-DD') }
    const res = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/tasks`, payload, {
      withCredentials: true
    });
    taskList.value.push(res.data)
    showAddDialog.value = false
    ElMessage.success('已加入月曆')
    fetchTasks()
  } catch (err) { ElMessage.error('新增失敗') }
}

const openEditDialog = (task) => { editingTask.value = { ...task }; showEditDialog.value = true }
const updateTask = async () => {
  try {
    // 確保 payload 包含 unit 與 title
    const payload = { 
      ...editingTask.value, 
      user_id: userId,
      date: dayjs(editingTask.value.date).format('YYYY-MM-DD') 
    }
    const res = await axios.patch(`${import.meta.env.VITE_API_BASE_URL}/tasks/${editingTask.value.id}`, payload, {
      withCredentials: true
    });
    
    // 更新本地列表，讓月曆即時顯示新內容
    const idx = taskList.value.findIndex(t => t.id === editingTask.value.id)
    if (idx !== -1) {
      taskList.value[idx] = res.data
    }
    
    showEditDialog.value = false
    ElMessage.success('更新成功')
  } catch (err) {
    console.error("更新失敗", err)
    ElMessage.error('儲存失敗，請檢查網路連線')
  }
}

const deleteTask = async (id) => {
  try {
    await axios.delete(`${import.meta.env.VITE_API_BASE_URL}/tasks/${id}`, { 
      params: { user_id: userId },
      withCredentials: true 
    });
    taskList.value = taskList.value.filter(t => t.id !== id)
    showEditDialog.value = false
    ElMessage.success('已移除任務')
  } catch (err) { console.error(err) }
}

const onDrop = async (date) => {
  if (!dragTask.value) return
  editingTask.value = { ...dragTask.value, date: formatDate(date) }
  await updateTask()
  dragTask.value = null; dragOverDate.value = null
}

const printCurrent = () => {
  const monthStr = currentMonth.value.format("YYYY年MM月")
  const start = currentMonth.value.startOf("month")
  const filtered = {}
  Object.entries(tasksByDate.value).forEach(([date, tasks]) => {
    if (dayjs(date).isSame(start, "month")) filtered[date] = tasks
  })
  exportMonthCalendarPDF(filtered, monthStr, `${monthStr}.pdf`)
}

onMounted(() => fetchTasks())
</script>

<style scoped>
/* 頁面背景與字體 */
.calendar-page { 
  padding: 20px; 
  background-color: #f0f2f5; 
  min-height: 100vh;
}

/* 1. 主卡片圓潤化 */
.calendar-card { 
  border-radius: 20px; /* 大圓角 */
  border: none; 
  background: #ffffff; 
  box-shadow: 0 8px 30px rgba(0,0,0,0.05); 
  padding: 10px;
}

.calendar-controls { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 15px 20px; 
  border-bottom: 1px solid #f0f0f0; 
  margin-bottom: 20px; 
}

h2 { font-weight: 800; color: #2c3e50; }

/* 2. 網格間距：讓格子「跳」出來 */
.calendar-grid { 
  display: grid; 
  grid-template-columns: repeat(7, 1fr); 
  background-color: transparent; /* 移除原本的灰色底色 */
  gap: 10px; /* 格子之間的間距 */
  padding: 5px;
}

.day-header { 
  background: transparent; 
  padding: 10px 0; 
  font-weight: 700; 
  color: #909399; 
}

/* 3. 日期格子圓角化 (最關鍵的部分) */
.calendar-cell { 
  background: #ffffff; 
  min-height: 150px; 
  border-radius: 15px; /* 格子圓角 */
  padding: 12px; 
  border: 1px solid #f0f2f5; /* 輕微邊框 */
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

/* 滑鼠懸停效果：讓格子有浮動感 */
.calendar-cell:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08);
  border-color: #409eff;
}

.calendar-cell.other-month { 
  background: #fafafa; 
  opacity: 0.5; 
  border: 1px dashed #e4e7ed;
}

/* 4. 今天日期的圓潤標記 */
.calendar-cell.is-today { 
  background: #f0f7ff; 
  border: 2px solid #409eff; 
}

.date-number { 
  font-weight: 900; 
  font-size: 1.1rem; 
  color: #303133; 
}

/* 5. 任務條圓角與配色優化 */
.task-item {
  font-size: 0.85rem; 
  padding: 6px 10px; 
  margin-bottom: 6px; 
  border-radius: 8px; /* 任務條圓角 */
  cursor: pointer;
  display: flex; 
  align-items: flex-start; 
  font-weight: 700; 
  transition: transform 0.1s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  border: none !important; /* 移除原本的 border-left 寫法改用背景 */
}

.task-item:hover { transform: scale(1.03); }

/* 配色系統 (柔和化) */
.chinese { background: #fff1f0; color: #cf1322; border-left: 4px solid #f5222d !important; }
.math    { background: #e6f7ff; color: #096dd9; border-left: 4px solid #1890ff !important; }
.english { background: #f9f0ff; color: #531dab; border-left: 4px solid #722ed1 !important; }
.social  { background: #fff7e6; color: #d46b08; border-left: 4px solid #fa8c16 !important; }
.science { background: #f6ffed; color: #389e0d; border-left: 4px solid #52c41a !important; }
.physics { background: #e6fffb; color: #006d75; border-left: 4px solid #13c2c2 !important; }
.art     { background: #fff0f6; color: #c41d7f; border-left: 4px solid #eb2f96 !important; }
.exam    { background: #feffe6; color: #ad8b00; border-left: 4px solid #fadb14 !important; }
.extra   { background: #fcffe6; color: #7cb305; border-left: 4px solid #a0d911 !important; }

.default-subject { background: #f5f5f5; color: #595959; border-left: 4px solid #8c8c8c !important; }

.is-done { 
  opacity: 0.4; 
  text-decoration: line-through; 
  filter: grayscale(0.8);
}

/* 列印與按鈕圓角 */
.el-button { border-radius: 10px; }
.current-month-display { border-radius: 10px !important; }

</style>
