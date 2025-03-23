<template>
  <div class="chat-input">
    <!-- Project Selector -->
    <div class="project-selector">
      <label for="project-select">Choose Project:</label>
      <div class="select-with-loading">
        <select id="project-select" v-model="selectedProject">
          <option v-for="project in projects" :key="project.id" :value="project.name">
            {{ project.name }}
          </option>
        </select>
        <label for="mode-select" style="margin-left: 10px;">Mode:</label>
        <select id="mode-select" v-model="selectedMode">
          <option value="Question Extraction">Question Extraction</option>
          <option value="Simple Answer Verbose">Simple Answer Verbose</option>
          <option value="Detailed Answer Verbose">Detailed Answer Verbose</option>
          <option value="Simple Answer">Simple Answer</option>
          <option value="Detailed Answer">Detailed Answer</option>
        </select>
        <!-- Loading Icon and Timer -->
        <div class="loading-with-timer" v-if="isLoading">
          <el-icon class="loading-icon">
            <Loading />
          </el-icon>
          <span>{{ timer }}s</span> <!-- Timer Display -->
        </div>
      </div>
    </div>

    <!-- Input and Send Button -->
    <div class="input-container">
      <input v-model="userInput" type="text" placeholder="Please enter a query..." @keyup.enter="sendMessage" />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script>
import { Loading } from '@element-plus/icons-vue';

export default {
  components: {
    Loading
  },
  props: {
    projects: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      userInput: '',
      selectedProject: '', // 选择的项目名称
      selectedMode: '',
      isLoading: false, // 控制 Loading 图标显示
      timer: 0, // 用于计时器的变量
      intervalId: null // 用于存储计时器的ID
    };
  },
  methods: {
    async sendMessage() {
      if (this.selectedProject && (this.selectedMode === 'Question Extraction' || this.userInput.trim())) {
        this.$emit('add-message', { sender: 'user', text: this.userInput });

        // 创建 FormData 对象
        const formData = new FormData();
        formData.append("project_name", this.selectedProject);

        // Only append query if the mode is not "Question Extraction"
        if (this.selectedMode !== 'Question Extraction') {
          formData.append("query", this.userInput);
        }

        if (this.selectedMode === 'Question Extraction') {
          this.$emit('add-message', { sender: 'user', text: "Question Extraction" });
        }
        
        // 清空输入框
        this.userInput = ''; 

        // 设置 isLoading 为 true 显示 Loading 图标
        this.isLoading = true;
        this.startTimer(); // 开始计时

        // 根据 selectedMode 选择不同的 API 路径
        let apiPath;
        switch (this.selectedMode) {
          case 'Question Extraction':
            apiPath = '/get_question/';
            break;
          case 'Simple Answer Verbose':
            apiPath = '/get_simple_answer_verbose/';
            break;
          case 'Detailed Answer Verbose':
            apiPath = '/get_detailed_answer_verbose/';
            break;
          case 'Simple Answer':
            apiPath = '/get_simple_answer/';
            break;
          case 'Detailed Answer':
            apiPath = '/get_detailed_answer/';
            break;
          default:
            console.warn('Invalid mode selected');
            return;
        }

        try {
          const response = await this.$request.post(apiPath, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });
          const answer = response.answer + "\n\n <strong>Total Response Time:</strong> " + this.timer + " seconds"
          this.$emit('add-message', { sender: 'bot', text: answer });
        } catch (error) {
          console.error('Error fetching answer:', error);
          this.$emit('add-message', { sender: 'bot', text: 'Error retrieving answer. Please try again later.' });
        } finally {
          // 请求结束后隐藏 Loading 图标
          this.isLoading = false;
          this.stopTimer(); // 停止计时
        }
      }
    },
    startTimer() {
      this.timer = 0;
      this.intervalId = setInterval(() => {
        this.timer += 1;
      }, 1000);
    },
    stopTimer() {
      clearInterval(this.intervalId);
      this.intervalId = null;
      this.timer = 0; // 重置计时器
    }
  }
};
</script>

<style scoped>
.loading-with-timer {
  display: flex;
  align-items: center;
}

.loading-with-timer .loading-icon {
  margin-right: 5px;
}
</style>


<style scoped>
.select-with-loading {
  display: flex;
  align-items: center;
}

.loading-icon {
  animation: rotating 2s linear infinite;
  margin-left: 8px;
}

.chat-input {
  display: flex;
  flex-direction: column;
  padding: 10px;
}
.project-selector {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.project-selector label {
  margin-right: 10px;
}
.project-selector select {
  padding: 5px;
  border-radius: 5px;
  border: 1px solid #ddd;
}
.input-container {
  display: flex;
  align-items: center;
}
.input-container input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-right: 10px;
}
.input-container button {
  padding: 10px 15px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>
