import axios from 'axios';
import { ElMessage } from 'element-plus';

// 建立實例
const service = axios.create({
  // 直接填入你確認過的後端網址
  baseURL: 'https://ai-self-study-manager.onrender.com', 
  //baseURL: import.meta.env.VITE_API_BASE_URL, 
  timeout: 10000,
  withCredentials: true 
});

// 【請求攔截器】在發出請求之前可以做的事
service.interceptors.request.use(
  config => {
    // 範例：如果 localStorage 有 token，就幫每個請求加上去
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers['Authorization'] = `Bearer ${token}`;
    // }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 【響應攔截器】在接收到後端資料後，先過濾一遍
service.interceptors.response.use(
  response => {
    // 這裡可以直接回傳 data，這樣頁面就不用寫 .data 了
    return response.data;
  },
  error => {
    // 統一處理錯誤訊息
    const message = error.response?.data?.error || '伺服器連線失敗';
    ElMessage.error(message);
    
    // 範例：如果後端回傳 401 (未登入)，就強制跳轉回登入頁
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);


export default service;
