<template>
  <div class="ai-piano-container">
    <div class="tabs">
      <button :class="['tab-btn', { active: activeTab === 'student' }]" @click="activeTab = 'student'">🎓 學生挑戰</button>
      <button :class="['tab-btn', { active: activeTab === 'teacher' }]" @click="activeTab = 'teacher'">👨‍🏫 老師管理</button>
    </div>

    <div class="main-card">
      <div v-if="activeTab === 'student'" class="mode-content">
        <h2>🎹 開始挑戰</h2>
        <div class="form-group">
          <label>選擇曲目</label>
          <select v-model="studentForm.musicId">
            <option value="" disabled>-- 請選擇 --</option>
            <option v-for="item in musicOptions" :key="item.id" :value="item.id">{{ item.title }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>上傳錄音 (.mp3)</label>
          <input type="file" @change="e => onFileChange(e, 'student')" accept="audio/mp3" />
        </div>
        <button class="action-btn student-btn" @click="startStudentCompare" :disabled="loading || !studentForm.musicId || !studentForm.file">
          {{ loading ? '分析中...' : '開始評分' }}
        </button>
      </div>

      <div v-else class="mode-content">
        <h2>🎼 建立標準檔</h2>
        <div class="form-group">
          <label>曲目名稱</label>
          <input type="text" v-model="teacherForm.title" placeholder="輸入曲名" />
        </div>
        <div class="form-row">
          <div class="form-group half">
            <label>速度 (BPM)</label>
            <input type="number" v-model="teacherForm.bpm" />
          </div>
          <div class="form-group half">
            <label>拍號</label>
            <select v-model="teacherForm.beats">
              <option value="4">4/4 拍</option>
              <option value="3">3/4 拍</option>
              <option value="2">2/4 拍</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>上傳示範音檔 (.mp3)</label>
          <input type="file" @change="e => onFileChange(e, 'teacher')" accept="audio/mp3" />
        </div>
        <button class="action-btn teacher-btn" @click="startTeacherUpload" :disabled="loading || !teacherForm.title || !teacherForm.file">
          建立並計算小節
        </button>
      </div>

      <div v-if="score !== null && !loading" class="result-area">
        <div class="score-container">
          <div class="score-badge">{{ score }}<small>分</small></div>
          <p class="summary-msg">{{ feedbackMsg }}</p>
        </div>

        <div v-if="comparisonDetails.length > 0" class="report-section">
          <h3>🔍 待改進明細 (點擊試聽音高)</h3>
          <div class="table-wrapper">
            <table class="report-table">
              <thead>
                <tr>
                  <th>小節</th>
                  <th>音高</th>
                  <th>狀況</th>
                  <th>改善建議</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in comparisonDetails" :key="idx" :class="{ 'row-error': item.status === 'missing' }">
                  <td class="measure-col">第 {{ item.measure }} 小節</td>
                  <td class="pitch-col">
                    <div class="pitch-capsule">
                      <span class="note-text">{{ item.pitch }}</span>
                      <button class="play-note-btn" @click="playNote(item.pitch)">🔊</button>
                    </div>
                  </td>
                  <td>
                    <span :class="['tag', item.status === 'missing' ? 'error' : 'warn']">
                      {{ item.status === 'missing' ? '❌ 漏彈' : '⚠️ 力度' }}
                    </span>
                  </td>
                  <td class="suggest-text">{{ item.suggestion }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <button class="reset-btn" @click="score = null">再次挑戰</button>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>AI 正在分析音符並轉換為音名...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';
import * as Tone from 'tone';

// 狀態管理
const activeTab = ref('student');
const loading = ref(false);
const score = ref(null);
const feedbackMsg = ref('');
const comparisonDetails = ref([]);
const musicOptions = ref([]);

const studentForm = reactive({ musicId: '', file: null });
const teacherForm = reactive({ title: '', file: null, bpm: 120, beats: 4 });

// 初始化 Tone.js 合成器 (用於試聽)
const synth = new Tone.Synth().toDestination();

// 1. 取得曲目列表
const fetchMusicList = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/music-list');
    musicOptions.value = res.data;
  } catch (err) {
    console.error("無法連線至後端伺服器");
  }
};

onMounted(fetchMusicList);

// 2. 處理檔案選取
const onFileChange = (e, type) => {
  const file = e.target.files[0];
  if (type === 'student') studentForm.file = file;
  else teacherForm.file = file;
};

// 3. 試聽音高功能
const playNote = async (noteName) => {
  if (!noteName || noteName === 'Unknown') return;
  await Tone.start(); // 啟動瀏覽器音訊上下文
  synth.triggerAttackRelease(noteName, "4n"); // 播放音符，持續 0.5 秒
};

// 4. 開始比對 (學生)
const startStudentCompare = async () => {
  loading.value = true;
  score.value = null;
  const fd = new FormData();
  fd.append('file', studentForm.file);
  fd.append('music_id', studentForm.musicId);

  try {
    const res = await axios.post('http://localhost:5000/api/analysis/compare', fd);
    score.value = res.data.score;
    feedbackMsg.value = res.data.message;
    comparisonDetails.value = res.data.details || [];
  } catch (err) {
    alert("分析過程發生錯誤，請檢查後端環境 (basic-pitch)");
  } finally {
    loading.value = false;
  }
};

// 5. 建立標準 (老師)
const startTeacherUpload = async () => {
  loading.value = true;
  const fd = new FormData();
  fd.append('file', teacherForm.file);
  fd.append('title', teacherForm.title);
  fd.append('bpm', teacherForm.bpm);
  fd.append('beats_per_measure', teacherForm.beats);

  try {
    await axios.post('http://localhost:5000/api/analysis/standard', fd);
    alert("標準檔建立成功！");
    fetchMusicList();
    activeTab.value = 'student';
  } catch (err) {
    alert("建立失敗");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.ai-piano-container { max-width: 650px; margin: 2rem auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
.tabs { display: flex; border-radius: 12px 12px 0 0; overflow: hidden; background: #e0e0e0; }
.tab-btn { flex: 1; padding: 1rem; border: none; cursor: pointer; font-weight: bold; font-size: 1rem; color: #666; transition: 0.3s; }
.tab-btn.active { background: #42b983; color: white; }

.main-card { background: white; padding: 2.5rem; border-radius: 0 0 12px 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }
.form-group { margin-bottom: 1.5rem; text-align: left; }
.form-row { display: flex; gap: 1rem; }
.half { flex: 1; }
label { display: block; margin-bottom: 0.5rem; font-weight: bold; color: #2c3e50; }
input, select { width: 100%; padding: 0.8rem; border: 1.5px solid #eee; border-radius: 8px; box-sizing: border-box; outline: none; transition: 0.3s; }
input:focus { border-color: #42b983; }

.action-btn { width: 100%; padding: 1.2rem; border: none; border-radius: 8px; color: white; font-weight: bold; font-size: 1.1rem; cursor: pointer; transition: 0.3s; }
.student-btn { background: #42b983; box-shadow: 0 4px 15px rgba(66, 185, 131, 0.3); }
.teacher-btn { background: #34495e; }
.action-btn:disabled { background: #ccc; cursor: not-allowed; box-shadow: none; }

.result-area { margin-top: 3rem; border-top: 2px solid #f9f9f9; padding-top: 2rem; }
.score-badge { font-size: 4rem; color: #42b983; font-weight: 900; line-height: 1; }
.score-badge small { font-size: 1.5rem; margin-left: 4px; }
.summary-msg { color: #7f8c8d; margin-top: 0.5rem; font-size: 1.1rem; }

/* 報告表格樣式 */
.report-section { text-align: left; margin-top: 2rem; }
.report-section h3 { font-size: 1.1rem; color: #2c3e50; margin-bottom: 1rem; }
.table-wrapper { max-height: 350px; overflow-y: auto; border: 1px solid #f0f0f0; border-radius: 8px; }
.report-table { width: 100%; border-collapse: collapse; }
.report-table th { background: #f8f9fa; padding: 12px; font-size: 0.9rem; position: sticky; top: 0; text-align: left; border-bottom: 2px solid #eee; }
.report-table td { padding: 12px; border-bottom: 1px solid #f9f9f9; font-size: 0.9rem; vertical-align: middle; }

.pitch-capsule { display: inline-flex; align-items: center; background: #f0f7f4; border: 1px solid #42b983; padding: 4px 12px; border-radius: 20px; gap: 8px; }
.note-text { font-family: monospace; font-weight: bold; color: #2c3e50; }
.play-note-btn { background: none; border: none; cursor: pointer; font-size: 1rem; padding: 0; line-height: 1; transition: 0.2s; }
.play-note-btn:hover { transform: scale(1.3); }

.tag { padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; color: white; }
.tag.error { background: #e74c3c; }
.tag.warn { background: #f39c12; }

.loading-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.9); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1000; }
.spinner { width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #42b983; border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 1.5rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.reset-btn { margin-top: 2rem; background: #eee; border: none; padding: 0.8rem 2rem; border-radius: 8px; cursor: pointer; font-weight: bold; color: #666; }
</style>