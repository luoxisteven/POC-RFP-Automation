import { createApp } from 'vue'
import App from './App.vue'
import request from './utils/request'
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';


// 创建应用实例
const app = createApp(App)

// 配置 axios 实例到全局属性
app.config.globalProperties.$request = request

// ElementPlus
app.use(ElementPlus);

// 挂载应用
app.mount('#app')