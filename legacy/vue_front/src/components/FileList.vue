<template>
  <!-- Company Profile Section -->
  <div class="project-list">
    <div class="header company-header">
      <h3>Company Profile</h3>
      <button class="add-btn" @click="triggerFileInput">+</button>
      <input type="file" ref="fileInput" @change="addCompanyProfile" style="display: none;" />
    </div>
    <ul>
      <li v-for="profile in companyProfiles" :key="profile.id" class="profile-item">
        <div class="profile-header">
          <span>{{ profile.name }}</span>
          <button class="delete-btn" @click="deleteCompanyProfile(profile.name)">-</button>
        </div>
      </li>
    </ul>

    <!-- Projects Section -->
    <div class="header">
      <h3>Projects</h3>
      <button class="add-btn" @click="addProject">+</button>
    </div>
    <ul>
      <li v-for="project in projects" :key="project.id" class="project-item">
        <div class="project-header">
          <span>{{ project.name }}</span>
          <div class="button-group">
            <el-upload
              class="upload-demo"
              :show-file-list="false"
              :on-change="(file) => addFile(project.name, file.raw)"
            >
              <button class="add-btn">+</button>
            </el-upload>
            <button class="delete-btn" @click="deleteProject(project.name)">-</button>
          </div>
        </div>
        <ul class="file-list">
          <li v-for="file in project.files" :key="file.id" class="file-item">
            <span>{{ file.name }}</span>
            <button class="delete-btn" @click="deleteFile(project.name, file.name)">-</button>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>


<script>
import { ElMessage, ElMessageBox } from 'element-plus';
export default {
  data() {
    return {
      selectedProjectName: '', // Store the project name when button is clicked
      companyProfiles: [],
      projects: []
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      try {
        const data = await this.$request.get('/get');

        // Company profile
        this.companyProfiles = data.company_profiles.map((name, index) => ({
          id: index + 1,
          name
        }));

        // Project Data
        this.projects = Object.keys(data.rfps).map((projectKey, index) => ({
          id: index + 1,
          name: projectKey,
          files: data.rfps[projectKey].map((fileName, fileIndex) => ({
            id: fileIndex + 1,
            name: fileName
          }))
        }));
        this.$emit('update-projects', this.projects); 

      } catch (error) {
        console.error("Error fetching data:", error);
      }
    }, 
    triggerFileInput() {
      this.$refs.fileInput.click(); // Triggers file input dialog
    },
    // triggerFileInput2() {
    //   this.$refs.fileInput2.click(); // Triggers file input dialog
    // },
    async addCompanyProfile(event) {
      const file = event.target.files[0];
      if (!file) return;
      console.log(file);
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await this.$request.post("/add_company_profile/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        if (response.status === "success") {
          // this.$message.success("File uploaded successfully")
          this.fetchData(); // Refreshes data after successful upload
        } else {
          // this.$message.error("Failed to upload file")
          console.error("Failed to upload file:", response.message);
        }
      } catch (error) {
        this.$message.error("Failed to upload file")
        console.error("Error uploading file:", error);
      } finally {
        event.target.value = ""; // Reset file input
      }
    },

    async deleteCompanyProfile(profileName) {
      try {
        const response = await this.$request.post("/del_company_profile/", {
          file_name: profileName, // Send file_name as required by the backend
        });

        // Check if the deletion was successful
        if (response.status === "success") {
          console.log(`File '${profileName}' deleted successfully.`);
          this.fetchData(); // Refresh data to update the UI
        } else {
          console.error("Failed to delete file:", response.message);
        }
      } catch (error) {
        console.error("Error deleting file:", error);
      }
    },

    async addProject() {
      try {
        // Prompt the user to input the project name
        const { value: projectName } = await ElMessageBox.prompt('Input your new project name', 'New Project', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
        });

        // If the user cancels, this part will not be reached, so we proceed only with a valid projectName
        if (projectName) {
          // Send the post request with the project name
          const response = await this.$request.post("/add_project/", {
            project_name: projectName, // Send file_name as required by the backend
          });

          // Check if the creation was successful
          if (response.status === "success") {
            console.log(`Created project '${projectName}' successfully.`);
            this.fetchData(); // Refresh data to update the UI
          } else {
            console.error("Failed to create project:", response.message);
          }
        }
      } catch (error) {
        // Handle cancel action or any other error
        ElMessage({
          type: 'info',
          message: 'Input canceled or an error occurred.',
        });
        console.error("Error creating project:", error);
      }
    },

    async deleteProject(projectName) {
      try {
        const response = await this.$request.post("/del_project/", {
          project_name: projectName, // Send file_name as required by the backend
        });
  
        // Check if the deletion was successful
        if (response.status === "success") {
          console.log(`File '${projectName}' deleted successfully.`);
          this.fetchData(); // Refresh data to update the UI
        } else {
          console.error("Failed to delete project:", response.message);
        }
      } catch (error) {
        console.error("Error deleting project:", error);
      }
    },
    
    
    async addFile(project_name, file) {

        const formData = new FormData();
        formData.append('project_name', project_name);
        formData.append('file', file);
        console.log(file);
        try {
          const response = await this.$request.post('/add_project_file/', formData, {
              headers: {
                  "Content-Type": "multipart/form-data",
              },
          });

          if (response.status === "success") {
              this.fetchData(); // Refresh data to update the UI
            } else {
              console.error("Failed to upload file:", response.message);
            }
        } catch (error) {
          console.error('File upload error:', error);
          alert('Error uploading file.');
        }
      },

    async deleteFile(projectName, fileName) {
      try {

        const formData = new FormData();
        formData.append("project_name", projectName);
        formData.append("file_name", fileName);

       const response = await this.$request.post("/del_project_file/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        // Check if the deletion was successful
        if (response.status === "success") {
          console.log(`File '${this.files}' deleted successfully.`);
          this.fetchData(); // Refresh data to update the UI
        } else {
          console.error("Failed to delete file:", response.message);
        }
      } catch (error) {
        console.error("Error deleting file:", error);
      }
    }
  }
};
</script>

<style scoped>
.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-list {
  width: 25%;
  background-color: #f9f9f9;
  padding: 20px;
  border-right: 1px solid #ddd;
  height: 100vh;
  overflow-y: auto;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 5px;
}

.company-header {
  margin-top: -10px; /* Adjust the value as needed to move the header up */
}


.header h3 {
  font-size: 1.2em;
  color: #333;
  margin-bottom: 15px;
}

.add-btn,
.delete-btn {
  background-color: #5cb85c;
  border: none;
  color: white;
  font-size: 1em;
  padding: 4px 8px;
  border-radius: 4px;
  width: 20px; /* 固定宽度 */
  height: 20px; /* 固定高度 */
  padding: 0px 1px; /* 统一内边距 */
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.add-btn:hover {
  background-color: #4cae4c;
}

.delete-btn {
  background-color: #d9534f;
  margin-left: 10px;
}

.delete-btn:hover {
  background-color: #c9302c;
}

.profile-item,
.project-item {
  background-color: #fff;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.profile-item:hover,
.project-item:hover {
  transform: scale(1.02);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.file-list {
  margin-top: 10px;
  padding-left: 15px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
}

.file-item span {
  max-width: calc(100% - 30px); /* 预留按钮空间，确保文件名不与按钮重叠 */
  word-wrap: break-word; 
  overflow-wrap: break-word;
  white-space: normal; /* 允许换行 */
}

.file-item .delete-btn {
  flex-shrink: 0; /* 防止按钮缩小 */
  margin-left: 10px;
}

.file-item:hover {
  background-color: #f1f1f1;
}

.button-group {
  display: flex;
  align-items: center;
}

.button-group .add-btn {
  margin-right: 2px; /* 控制按钮之间的间距 */
}

</style>
