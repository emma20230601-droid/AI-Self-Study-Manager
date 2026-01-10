<template>
  <div class="calendar-page">
    <el-card class="calendar-card" shadow="never">
      <div class="calendar-controls">
        <div class="title-section">
          <h2>📅 學習成就月曆</h2>
          <span class="sub-title hidden-xs-only">雙擊日期新增，單擊編輯，拖拽任務可調整日期</span>
        </div>
        
        <div class="action-section">
          <el-button-group>
            <el-button @click="goToPreviousMonth" :icon="ArrowLeft">上個月</el-button>
            <el-button class="current-month-display">
              {{ currentMonth.format('YYYY 年 MM 月') }}
            </el-button>
            <el-button @click="goToNextMonth">下個月<el-icon class="el-icon--right"><ArrowRight /></el-icon></el-button>
          </el-button-group>
          <el-button type="success" @click="printCurrent" :icon="Printer" plain style="margin-left: 10px">列印本月報表</el-button>
        </div>
      </div>

      <div class="calendar-grid desktop-only">
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
          <div class="cell-top"><span class="date-number">{{ date.date() }}</span></div>
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

      <div class="mobile-only">
  <div class="mobile-fixed-header">
    <div class="mobile-date-scroller">
      <div 
        v-for="date in currentMonthDays" 
        :key="formatDate(date)"
        class="mobile-date-item"
        :class="{ 'active': formatDate(date) === selectedDate, 'is-today': isToday(date) }"
        @click="selectedDate = formatDate(date)"
      >
        <span class="m-day">{{ weekDays[date.day()].replace('週', '') }}</span>
        <span class="m-date">{{ date.date() }}</span>
        <div v-if="(tasksByDate[formatDate(date)] || []).length > 0" class="m-dot"></div>
      </div>
    </div>
  </div>

  <div class="mobile-scroll-content">
    <div class="mobile-task-view">
      <div class="view-header">
        <span>{{ dayjs(selectedDate).format('MM/DD') }} 任務清單</span>
        <el-button type="primary" size="small" circle :icon="Plus" @click="openAddDialog(dayjs(selectedDate))" />
      </div>
      <div v-if="(tasksByDate[selectedDate] || []).length === 0" class="empty-hint">本日無任務</div>
      <div
        v-for="task in tasksByDate[selectedDate] || []"
        :key="task.id"
        class="mobile-task-card"
        :class="[getSubjectClass(task.subject), { 'is-done': task.status === '已完成' }]"
        @click="openEditDialog(task)"
      >
        <div class="m-card-left">
          <span class="m-task-type">[{{ task.type }}]</span>
          <div class="m-task-title"><strong>{{ task.subject }}</strong>：{{ task.title }}</div>
        </div>
        <span class="m-status-icon">{{ getStatusIcon(task.status) }}</span>
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
          <el-input v-model="newTask.unit" placeholder="例如：第一單元、分數的乘法、期中考範圍" />
        </el-form-item>
        <el-form-item label="詳細內容">
          <el-input v-model="newTask.title" type="textarea" :rows="3" placeholder="請輸入頁碼、講義範圍或是具體的錯題內容..." />
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
          <el-input v-model="editingTask.unit" placeholder="例如：第一單元、分數的乘法、期中考範圍" />
        </el-form-item>

        <el-form-item label="詳細內容">
          <el-input v-model="editingTask.title" type="textarea" :rows="3" placeholder="請輸入頁碼、講義範圍或是具體的錯題內容..." />
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
              <el-date-picker v-model="editingTask.date" type="date" style="width:100%" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
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
import { ArrowLeft, ArrowRight, Printer, Plus } from '@element-plus/icons-vue'
import { exportMonthCalendarPDF } from "@/utils/exportCalendarPdf";

const API_BASE = import.meta.env.VITE_API_BASE_URL;
const userId = parseInt(localStorage.getItem('user_id'))
const currentMonth = ref(dayjs())
const taskList = ref([])
const selectedDate = ref(dayjs().format('YYYY-MM-DD'))

const weekDays = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']
const formatDate = (d) => dayjs(d).format('YYYY-MM-DD')
const subjectOrder = ['國語', '數學', '英文', '社會', '自然', '理化', '生物', '其它', '藝術', '國中入學考', '小科加課']
const typeOrder = ['自修', '評量', '學校課本', '學校作業', '考卷', '小科', '加深加廣', '戶外活動', '考試', '報名']

const fetchTasks = async () => {
  try {
    const res = await axios.get(`${API_BASE}/tasks?user_id=${userId}`)
    taskList.value = res.data.sort((a, b) => {
      const aSub = subjectOrder.indexOf(a.subject), bSub = subjectOrder.indexOf(b.subject)
      if (aSub !== bSub) return aSub - bSub
      return new Date(a.date) - new Date(b.date)
    })
  } catch (err) { console.error(err) }
}

const tasksByDate = computed(() => {
  const map = {}
  taskList.value.forEach(task => { if (!map[task.date]) map[task.date] = []; map[task.date].push(task) })
  return map
})

const calendarDays = computed(() => {
  const start = currentMonth.value.startOf('month').startOf('week')
  const end = currentMonth.value.endOf('month').endOf('week')
  const days = []; let date = start
  while (date.isBefore(end) || date.isSame(end)) { days.push(date); date = date.add(1, 'day') }
  return days
})

const currentMonthDays = computed(() => {
  const start = currentMonth.value.startOf('month')
  return Array.from({ length: currentMonth.value.daysInMonth() }, (_, i) => start.add(i, 'day'))
})

const goToPreviousMonth = () => { currentMonth.value = currentMonth.value.subtract(1, 'month') }
const goToNextMonth = () => { currentMonth.value = currentMonth.value.add(1, 'month') }
const isToday = (date) => dayjs().isSame(date, 'day')
const getStatusIcon = (status) => (status === '已完成' ? '✅' : status === '進行中' ? '⏳' : '☐')

const getSubjectClass = (subject) => {
  const map = { 國語:'chinese', 數學:'math', 社會:'social', 自然:'science', 理化:'physics', 生物:'biology', 英文:'english', 藝術:'art', 國中入學考:'exam', 小科加課:'extra' }
  for (const key in map) if (subject.includes(key)) return map[key]
  return 'default-subject'
}

const showAddDialog = ref(false), showEditDialog = ref(false)
const newTask = ref({ subject: '數學', type: '自修', unit: '', title: '', date: '', status: '未開始' })
const editingTask = ref(null), dragTask = ref(null), dragOverDate = ref(null)

const openAddDialog = (date) => {
  newTask.value = { subject: '數學', type: '自修', unit: '', title: '', date: formatDate(date), status: '未開始' }
  showAddDialog.value = true
}

const addTask = async () => {
  try {
    const payload = { ...newTask.value, user_id: userId, date: dayjs(newTask.value.date).format('YYYY-MM-DD') }
    const res = await axios.post(`${API_BASE}/tasks`, payload)
    taskList.value.push(res.data); showAddDialog.value = false; ElMessage.success('已加入'); fetchTasks()
  } catch (err) { ElMessage.error('新增失敗') }
}

const openEditDialog = (task) => { editingTask.value = { ...task }; showEditDialog.value = true }
const updateTask = async () => {
  try {
    const payload = { ...editingTask.value, user_id: userId, date: dayjs(editingTask.value.date).format('YYYY-MM-DD') }
    const res = await axios.patch(`${API_BASE}/tasks/${editingTask.value.id}`, payload)
    const idx = taskList.value.findIndex(t => t.id === editingTask.value.id)
    if (idx !== -1) taskList.value[idx] = res.data
    showEditDialog.value = false; ElMessage.success('更新成功')
  } catch (err) { ElMessage.error('儲存失敗') }
}

const deleteTask = async (id) => {
  try {
    await axios.delete(`${API_BASE}/tasks/${id}`, { params: { user_id: userId } })
    taskList.value = taskList.value.filter(t => t.id !== id); showEditDialog.value = false
    ElMessage.success('已移除任務')
  } catch (err) { console.error(err) }
}

const onDrop = async (date) => {
  if (!dragTask.value) return
  editingTask.value = { ...dragTask.value, date: formatDate(date) }
  await updateTask(); dragTask.value = null; dragOverDate.value = null
}

const printCurrent = () => {
  const monthStr = currentMonth.value.format("YYYY年MM月")
  exportMonthCalendarPDF(tasksByDate.value, monthStr)
}

onMounted(() => fetchTasks())
</script>

<style scoped>
/* ==========================================================================
   1. 通用樣式 (電腦/手機共用)
   ========================================================================== */
.calendar-page { 
  padding: 20px; 
  background-color: #f0f2f5; 
  min-height: 100vh; 
  width: 100%;
  box-sizing: border-box;
}

.calendar-card { 
  border-radius: 20px; 
  border: none; 
  background: #ffffff; 
  box-shadow: 0 8px 30px rgba(0,0,0,0.05); 
}

/* 狀態樣式 */
.is-done { opacity: 0.5 !important; }
.is-done .task-content, .is-done .m-task-title, .is-done strong { 
  text-decoration: line-through !important; 
}

/* 科目配色 */
.chinese { background: #fff1f0; color: #cf1322; border-left: 4px solid #f5222d !important; }
.math    { background: #e6f7ff; color: #096dd9; border-left: 4px solid #1890ff !important; }
.english { background: #f9f0ff; color: #531dab; border-left: 4px solid #722ed1 !important; }
.social  { background: #fff7e6; color: #d46b08; border-left: 4px solid #fa8c16 !important; }
.science { background: #f6ffed; color: #389e0d; border-left: 4px solid #52c41a !important; }
.physics { background: #e6fffb; color: #006d75; border-left: 4px solid #13c2c2 !important; }
.art     { background: #fff0f6; color: #c41d7f; border-left: 4px solid #eb2f96 !important; }
.exam    { background: #feffe6; color: #ad8b00; border-left: 4px solid #fadb14 !important; }
.extra   { background: #fcffe6; color: #7cb305; border-left: 4px solid #a0d911 !important; }

/* ==========================================================================
   2. 電腦版佈局 (維持原樣，不作任何變更)
   ========================================================================== */
.desktop-only { 
  display: grid; 
  grid-template-columns: repeat(7, 1fr); 
  gap: 10px; 
  padding: 10px; 
}
.mobile-only { display: none; }

.calendar-controls { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  padding: 15px 20px; 
  border-bottom: 1px solid #f0f0f0; 
  margin-bottom: 20px; 
}

.calendar-cell { 
  background: #ffffff; 
  min-height: 150px; 
  border-radius: 15px; 
  padding: 12px; 
  border: 1px solid #f0f2f5; 
}

.calendar-cell.is-today { background: #f0f7ff; border: 2px solid #409eff; }

.task-item {
  font-size: 0.85rem; padding: 6px 10px; margin-bottom: 6px; 
  border-radius: 8px; cursor: pointer; display: flex; font-weight: 700; 
}

/* ==========================================================================
   3. 手機版滿版修正 (僅在手機螢幕下生效)
   ========================================================================== */
@media (max-width: 768px) {
  /* A. 徹底鎖死水平溢出 */
  :global(html), :global(body) {
    overflow-x: hidden !important;
    position: relative;
    width: 100%;
    background-color: #ffffff !important; /* 強制改為白底 */
  }

  .calendar-page { 
    padding: 0 !important; 
    margin: 0 !important;
    width: 100% !important; /* 改用 100% 避免 100vw 在含捲軸瀏覽器下的計算錯誤 */
    max-width: 100vw !important;
    display: block !important;
    overflow-x: hidden !important; /* 禁止任何東西超出這個範圍 */
    background-color: #ffffff !important; /* 強制改為白底 */
  }

  /* B. 移除卡片內縮並確保寬度不超標 */
  :deep(.el-card) { 
    border: none !important; 
    border-radius: 0 !important; 
    width: 100% !important;
    box-shadow: none !important;
  }
  :deep(.el-card__body) { 
    padding: 0 !important; 
    width: 100% !important;
    box-sizing: border-box;
  }

  :deep(.el-main) {background-color: #ffffff !important;}

  .desktop-only { display: none !important; }
  .mobile-only { 
    display: flex !important; 
    flex-direction: column; 
    width: 100% !important; 
    overflow-x: hidden;
  }

  /* C. 控制區鎖定 */
  .calendar-controls { 
    flex-direction: column; 
    padding: 15px; 
    width: 100% !important; 
    box-sizing: border-box; 
    margin: 0 !important;
    border-bottom: 1px solid #f0f0f0;
  }
  .action-section { 
    width: 100%; 
    margin-top: 10px;
    box-sizing: border-box;
  }
  .action-section .el-button-group { 
    display: flex; 
    width: 100%; 
  }
  .action-section .el-button { 
    flex: 1; 
  }

  /* D. 日期捲軸：唯一允許水平滑動的部分 */
  .mobile-date-scroller {
    width: 100% !important;
    display: flex;
    overflow-x: auto; /* 僅此處允許左右 */
    padding: 15px 10px;
    background: #fcfcfc;
    border-bottom: 1px solid #eee;
    box-sizing: border-box;
    -webkit-overflow-scrolling: touch;
  }
  .mobile-date-scroller::-webkit-scrollbar { display: none; } /* 隱藏捲軸防止佔位 */

  .mobile-date-item {
    flex: 0 0 auto; /* 改為自動寬度，由 min-width 控制 */
    min-width: 60px;
    margin: 0 5px;
  }

  /* E. 任務清單區：強制撐開但不溢出 */
  .mobile-task-view {
    width: 100% !important;
    padding: 20px 15px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    overflow-x: hidden;
  }

  .mobile-task-card {
    width: 100% !important; 
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    margin-bottom: 12px;
    margin-left: 0 !important;
    margin-right: 0 !important;
    box-sizing: border-box; 
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  }
  /* 4. 針對「本日無任務」的提示文字優化 (既然背景是白的，文字可以稍微淡一點) */
  .empty-hint {
    text-align: center;
    color: #909399;
    padding: 40px 0;
    font-size: 14px;
    background-color: #ffffff; /* 確保提示區域不帶灰 */
  }

  /* 5. 日期滑動軸背景也改為純白，讓整體視覺更一致 */
  .mobile-fixed-header,
  .mobile-date-scroller {
    background-color: #ffffff !important;
  }

  /* F. 對話框與 Row 修正 (修正水平動的最關鍵處) */
  :deep(.el-dialog) { 
    width: 92% !important; 
    margin: 5vh auto !important; 
    max-width: 100vw;
  }
  :deep(.el-row) {
    margin-left: 0 !important;  /* 強制移除 Element Plus 的負 margin */
    margin-right: 0 !important; /* 強制移除 Element Plus 的負 margin */
    width: 100% !important;
    display: flex;
    flex-wrap: wrap;
  }
  :deep(.el-col) {
    padding: 0 !important; /* 確保內容不被 padding 撐開 */
  }
  :deep(.el-col-12) { 
    width: 100% !important; 
    margin-bottom: 10px;
  }
}
</style>