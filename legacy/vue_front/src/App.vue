<template>
  <div class="app-container">
    <FileList @updateProjects="updateProjects"/>
    <div class="chat-container">
      <ChatBox :messages="messages" />
      <ChatInput :projects="projects" @add-message="addMessageToChatBox"/>
    </div>
  </div>
</template>

<script>
import FileList from './components/FileList.vue';
import ChatBox from './components/ChatBox.vue';
import ChatInput from './components/ChatInput.vue';

export default {
  components: { FileList, ChatBox, ChatInput },
  data() {
    return {
      messages: [
        {
          sender: 'sys',
          text: '<strong>Guidelines:</strong> \n1) Add or delete projects or files from the menu on the left;\n2) Select your project and mode from the dropdown lists below;\n3) Enter a query related to the selected project.\n\n<strong>Please be patient!\n\nA simple answer takes 3 to 10 minutes, while a detailed answer takes 5 to 15 minutes.</strong>'
        }
      ],
      projects: []
    };
  },
  methods: {
    updateProjects(updatedProjects) {
      this.projects = updatedProjects;
    },
    addMessageToChatBox(message) {
      // 更新消息数组，这会触发 ChatBox 的更新
      this.messages.push(message);
    }
  }
};
</script>


<style>
*{
  font-family: Helvetica
}


html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.app-container {
  display: flex;
  width: 100vw;
  height: 100vh;
}

.chat-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

/* .file-list {
  width: 40%;
  height: 100%;
  overflow-: auto;
  overflow-y: auto;
} */
</style>
