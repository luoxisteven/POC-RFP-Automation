<template>
  <div class="chat-box">
    <div v-for="(message, index) in messages" :key="index" class="message">
      <div :class="{'user-message': message.sender === 'user', 'bot-message': message.sender === 'bot', 'sys-message': message.sender === 'sys'}" v-html="formatMessage(message.text)">
      </div>
    </div>
  </div>
</template>

<script>
// import { marked } from 'marked';

export default {
  props: {
    messages: {
      type: Array,
      required: true
    }
  },
  methods: {
    formatMessage(text) {
      // 使用 marked 将文本渲染为 Markdown 格式的 HTML
      return text;
    }
  }
};
</script>

<style scoped>
.chat-box {
  width: 80%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  height: calc(100vh - 60px);
}
.message {
  margin: 10px 0;
}
.user-message {
  background-color: #e0f7fa;
  padding: 10px;
  border-radius: 5px;
  align-self: flex-end;
  max-width: 60%;
  white-space: pre-wrap;
}
.bot-message {
  background-color: #ffecb3;
  padding: 10px;
  border-radius: 5px;
  align-self: flex-start;
  max-width: 60%;
  white-space: pre-wrap;
}

.sys-message {
  background-color: #ffcdd2;
  padding: 10px;
  border-radius: 5px;
  align-self: center;
  max-width: 60%;
  white-space: pre-wrap;
}

/* 添加样式来适应 Markdown 格式，例如粗体、标题等 */
.message h1, .message h2, .message h3 {
  margin: 0;
  font-weight: bold;
}
.message p {
  margin: 0;
}

</style>
