<template>
  <div class="missing-tasks-container">
    <el-card class="main-card-full">
      <div class="page-header">
        <div class="title-wrap">
          <h2>🎯 進度衝刺看板</h2>
          <div class="header-hint">檢視未完成任務，補齊缺口，讓學習不留死角</div>
        </div>

        <div class="filter-section">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="開始日期"
            end-placeholder="結束日期"
            format="YYYY/MM/DD"
            value-format="YYYY-MM-DD"
            size="large"
            @change="loadTasks"
            style="width: 350px"
          />

          <el-select v-model="selectedSubject" placeholder="全部科目" size="large" clearable style="width: 150px">
            <el-option label="全部科目" value="" />
            <el-option v-for="sub in allSubjects" :key="sub" :label="sub" :value="sub" />
          </el-select>

          <el-select v-model="selectedFilter" placeholder="快捷篩選" size="large" @change="loadTasks" style="width: 180px">
            <el-option label="截止前未完成" value="deadline" />
            <el-option label="期中考進度" value="midterm" />
            <el-option label="期末考進度" value="final" />
            <el-option label="自定義區間" value="custom" />
          </el-select>
        </div>
      </div>

      <div class="table-scroll-area">
        <div class="section-title">
          <span class="icon">📘</span> 核心進度 (國/數/英/社/自)
          <el-tag type="danger" v-if="filteredCoreTasks.length" effect="dark" round>
            {{ filteredCoreTasks.length }} 項待完成
          </el-tag>
        </div>
        
        <el-table :data="filteredCoreTasks" border stripe class="custom-table core-border">
          <el-table-column label="科目" width="110" align="center">
            <template #default="scope">
              <span class="subject-label" :class="getSubjectClass(scope.row.subject)">{{ scope.row.subject }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="類型" width="120" align="center" />
          <el-table-column prop="unit" label="單元" width="250" />
          <el-table-column prop="title" label="內容" min-width="200" />
          <el-table-column label="截止日期" width="140" align="center">
            <template #default="scope">
              <span :class="{'overdue': isOverdue(scope.row.target_date)}">
                {{ scope.row.target_date || '未定' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="目前完成度" width="180">
            <template #default="scope">
              <el-progress 
                :percentage="scope.row.progress_percent" 
                :status="scope.row.progress_percent > 80 ? 'warning' : 'exception'" 
                :stroke-width="12"
              />
            </template>
          </el-table-column>
        </el-table>
        <div v-if="filteredCoreTasks.length === 0" class="empty-status">
          🎉 太棒了！核心科目進度都在掌控中。
        </div>

        <div class="section-title mt-30">
          <span class="icon">📗</span> 延伸任務 (生物/理化/藝術/其他)
        </div>
        <el-table :data="filteredOtherTasks" border stripe class="custom-table other-border">
          <el-table-column label="科目" width="110" align="center">
            <template #default="scope">
              <span class="subject-label" :class="getSubjectClass(scope.row.subject)">{{ scope.row.subject }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="類型" width="120" align="center" />
          <el-table-column prop="unit" label="單元" width="250" />
          <el-table-column prop="title" label="內容" min-width="200" />
          <el-table-column prop="target_date" label="截止日期" width="140" align="center" />
          <el-table-column label="完成度" width="180">
            <template #default="scope">
              <el-progress 
                :percentage="scope.row.progress_percent" 
                color="#67c23a"
                :stroke-width="10"
              />
            </template>
          </el-table-column>
        </el-table>
        <div v-if="filteredOtherTasks.length === 0" class="empty-status">
          ☕ 目前沒有待補辦的其他任務。
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import dayjs from 'dayjs'
import isBetween from 'dayjs/plugin/isBetween'
import { ElMessage } from 'element-plus'

dayjs.extend(isBetween)

const userId = parseInt(localStorage.getItem('user_id'))
const coreTasks = ref([])
const otherTasks = ref([])
const dateRange = ref([])

const selectedSubject = ref('')
const selectedFilter = ref('deadline')
const allSubjects = ['國語','數學','英文','社會','自然','生物','理化','藝術','其它']

const coreSubjects = ['國語','數學','英文','社會','自然']
const coreTypes = ['自修','評量','學校課本','學校作業','考卷']

// --- 新增：動態日期處理 ---
const getTargetExamDates = async () => {
  // 1. 先從 LocalStorage 拿
  let midterm = localStorage.getItem('midterm_date')
  let final = localStorage.getItem('final_date')

  // 2. 如果 LocalStorage 沒有，則從 API 抓取
  if (!midterm || !final) {
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/tasks`, {
        params: { user_id: userId },
        withCredentials: true
      });
      if (res.data) {
        midterm = res.data.midterm_date
        final = res.data.final_date
        // 補存入快取
        localStorage.setItem('midterm_date', midterm || '')
        localStorage.setItem('final_date', final || '')
      }
    } catch (err) {
      console.error("抓取考期失敗", err)
    }
  }
  return { 
    midterm: midterm ? dayjs(midterm) : null, 
    final: final ? dayjs(final) : null 
  }
}

const loadTasks = async () => {
  if (!userId) { ElMessage.warning('請先登入'); return }

  try {
    // 獲取最新的考期設定
    const { midterm, final } = await getTargetExamDates()
    
    const res = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/progress/with_tasks`, {
      params: { user_id: userId },
      withCredentials: true
    });
    const allTasks = res.data
    const today = dayjs().startOf('day')

    const filterByType = (task) => {
      const target = task.target_date ? dayjs(task.target_date) : null
      const progressIncomplete = Number(task.progress_percent) < 100
      if (!progressIncomplete) return false

      // 1. 自定義區間日期篩選
      if (dateRange.value && dateRange.value.length === 2) {
        return target ? target.isBetween(dateRange.value[0], dateRange.value[1], 'day', '[]') : false
      }

      // 2. 快捷篩選 (動態日期)
      if (selectedFilter.value === 'deadline') {
        return target ? target.isBefore(today.add(1, 'day')) : true
      }
      if (selectedFilter.value === 'midterm') {
        // 若沒設定期中考日期，則不顯示
        return (midterm && target) ? target.isBefore(midterm.add(1, 'day')) : (selectedFilter.value !== 'midterm')
      }
      if (selectedFilter.value === 'final') {
        return (final && target) ? target.isBefore(final.add(1, 'day')) : (selectedFilter.value !== 'final')
      }
      return true
    }

    const filteredTasks = allTasks.filter(filterByType)

    coreTasks.value = filteredTasks.filter(t => coreSubjects.includes(t.subject) && coreTypes.includes(t.type))
    otherTasks.value = filteredTasks.filter(t => !(coreSubjects.includes(t.subject) && coreTypes.includes(t.type)))

    const sortFn = (a, b) => {
      const da = a.target_date ? dayjs(a.target_date) : dayjs('2099-12-31')
      const db = b.target_date ? dayjs(b.target_date) : dayjs('2099-12-31')
      return da.diff(db)
    }

    coreTasks.value.sort(sortFn)
    otherTasks.value.sort(sortFn)

  } catch (err) { console.error('載入失敗', err) }
}

const isOverdue = (dateStr) => {
  if (!dateStr) return false
  return dayjs(dateStr).isBefore(dayjs().startOf('day'))
}

const getSubjectClass = (subject) => {
  const map = { '國語':'chinese', '數學':'math', '英文':'english', '社會':'social', '自然':'science' }
  return map[subject] || 'other-sub'
}

onMounted(loadTasks)

const filteredCoreTasks = computed(() => {
  return selectedSubject.value ? coreTasks.value.filter(t => t.subject === selectedSubject.value) : coreTasks.value
})

const filteredOtherTasks = computed(() => {
  return selectedSubject.value ? otherTasks.value.filter(t => t.subject === selectedSubject.value) : otherTasks.value
})
</script>

<style scoped>
/* 原有樣式保持不變 */
.missing-tasks-container { padding: 15px; background-color: #f4f7f9; min-height: calc(100vh - 40px); }
.main-card-full { border-radius: 15px; border: none; min-height: calc(100vh - 70px); }
.page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #f0f2f5; }
h2 { font-size: 2rem; font-weight: 800; color: #1a1a1a; margin: 0; }
.header-hint { color: #909399; margin-top: 5px; font-size: 1rem; }
.filter-section { display: flex; gap: 15px; }
.section-title { font-size: 1.3rem; font-weight: 700; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; color: #2c3e50; }
.mt-30 { margin-top: 40px; }
.custom-table { border-radius: 8px; overflow: hidden; }
.core-border { border-top: 4px solid #f56c6c; }
.other-border { border-top: 4px solid #67c23a; }
.subject-label { padding: 4px 10px; border-radius: 4px; font-weight: 700; color: white; }
.overdue { color: #f56c6c; font-weight: 800; text-decoration: underline; }
.empty-status { text-align: center; padding: 30px; color: #909399; font-style: italic; background: #fdfdfd; border: 1px dashed #dcdfe6; border-radius: 8px; margin-top: 10px; }
.chinese { background: #d32f2f; }
.math { background: #1976d2; }
.english { background: #7b1fa2; }
.social { background: #ef6c00; }
.science { background: #2e7d32; }
.other-sub { background: #607d8b; }

</style>
