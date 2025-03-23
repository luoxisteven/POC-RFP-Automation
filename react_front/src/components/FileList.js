import "../App"
// import React, { useState, useEffect, useCallback, useRef } from "react";
import { useState, useEffect, useCallback, useRef, Fragment } from "react";
import { Typography, Snackbar, Alert  } from "@mui/material";

import request from "../utils/request";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import ListSubheader from "@mui/material/ListSubheader";
import IconButton from "@mui/material/IconButton";
import Collapse from "@mui/material/Collapse";
import ExpandLess from "@mui/icons-material/ExpandLess";
import ExpandMore from "@mui/icons-material/ExpandMore";
import AddIcon from "@mui/icons-material/Add";
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';

import FileUploadIcon from "@mui/icons-material/FileUpload";

import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";

import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

const FileList = ({ updateProjects }) => {
  const [companyProfiles, setCompanyProfiles] = useState([]);
  const [projects, setProjects] = useState([]);
  const [openProjects, setOpenProjects] = useState({});
  const fileInputRef = useRef(null);

  // New Project Dialog
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const handleDialogOpen = () => setDialogOpen(true);
  const handleDialogClose = () => {
    setDialogOpen(false);
    setNewProjectName("");
  };

  // Delete Dialog
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState({ type: "", project: "", name: "" });

  const handleDelete = (type, project, name) => {
    setDeleteTarget({ type, project, name });
    setDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    if (deleteTarget.type === "profile") {
      deleteCompanyProfile(deleteTarget.name);
    } else if (deleteTarget.type === "project") {
      deleteProject(deleteTarget.project);
    } else if (deleteTarget.type === "file"){
      deleteFile(deleteTarget.project, deleteTarget.name)
    }
    setDeleteDialogOpen(false);
    setDeleteTarget({ type: "", name: "" });
  };

  // Snackbar Alert
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  const handleSnackbarClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbarOpen(false);
  };

  // 封装的函数
  const showSnackbar = (severity, message) => {
    setSnackbarSeverity(severity);
    setSnackbarMessage(message);
    setSnackbarOpen(true);
  };

  // Fetch data from the backend
  const fetchData = useCallback(async () => {
    try {
      const data = await request.get("/get");
      setCompanyProfiles(
        data.company_profiles.map((name, index) => ({
          id: index + 1,
          name,
        }))
      );
      const projectList = Object.keys(data.rfps).map((projectKey, index) => ({
        id: index + 1,
        name: projectKey,
        files: data.rfps[projectKey].map((fileName, fileIndex) => ({
          id: fileIndex + 1,
          name: fileName,
        })),
      }));
      setProjects(projectList);
      updateProjects(projectList);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  }, [updateProjects]);

  const [hasFetched, setHasFetched] = useState(false);

  useEffect(() => {
    if (!hasFetched) {
      fetchData();
      setHasFetched(true);
    }
  }, [fetchData, hasFetched]);

  // Toggle project collapse
  const toggleProjectOpen = (projectId) => {
    setOpenProjects((prevState) => ({
      ...prevState,
      [projectId]: !prevState[projectId],
    }));
  };

  // Handle file input click
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  // Add a new company profile
  const addCompanyProfile = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const result = await request.post("/add_company_profile/", formData);
      if (result.status === "success") {
        fetchData();
        showSnackbar("success", "File uploaded successfully!");
      } else {
        showSnackbar("error", `Failed to upload file: ${result.message}`);
      }
    } catch (error) {
      showSnackbar("error", "Error uploading file!");
    } finally {
      event.target.value = "";
    }
  };

  // Delete a company profile
  const deleteCompanyProfile = async (profileName) => {
    try {
      const result = await request.post("/del_company_profile/", {
        file_name: profileName,
      });
      if (result.status === "success") {
        fetchData();
        showSnackbar("success", "Company profile deleted successfully!");
      } else {
        showSnackbar("error", `Failed to delete file: ${result.message}`);
      }
    } catch (error) {
      showSnackbar("error", "Error deleting file!");
    }
  };

  const addProject = async () => {
    if (!newProjectName) return; // 检查项目名称是否为空
    try {
      const result = await request.post("/add_project/", { project_name: newProjectName });
      if (result.status === "success") {
        fetchData(); // 刷新项目列表
        handleDialogClose(); // 关闭对话框
        showSnackbar("success", "Project created successfully!");
      } else {
        showSnackbar("error", `Failed to create project: ${result.message}`);
      }
    } catch (error) {
      showSnackbar("error", "Error creating project!");
    }
  };
  
  // Delete a project
  const deleteProject = async (projectName) => {
    try {
      const result = await request.post("/del_project/", { project_name: projectName });
      if (result.status === "success") {
        fetchData();
        showSnackbar("success", "Project deleted successfully!");
      } else {
        showSnackbar("error", `Failed to delete project: ${result.message}`);
      }
    } catch (error) {
      showSnackbar("error", "Error deleting project!");
    }
  };

  // Add a file to a project
  const addFile = async (projectName, file) => {
    const formData = new FormData();
    formData.append("project_name", projectName);
    formData.append("file", file);
    try {
      const result = await request.post("/add_project_file/", formData);
      if (result.status === "success") {
        fetchData();
        showSnackbar("success", "File added successfully!");
      } else {
        showSnackbar("error", `Failed to upload file: ${result.message}`);
      }
    } catch (error) {
      showSnackbar("error", "File upload error!");
    }
  };

  // Delete a file from a project
  const deleteFile = async (projectName, fileName) => {
    const formData = new FormData();
    formData.append("project_name", projectName);
    formData.append("file_name", fileName);
    try {
      const result = await request.post("/del_project_file/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (result.status === "success") {
        fetchData();
        showSnackbar("success", "File deleted successfully!");
      } else {
        showSnackbar("error", `Failed to delete file: ${result.message}`);
      }
    } catch (error) {
      showSnackbar("error", "Error deleting file!");
    }
  };

  return (
    <div
      className="filelist-container"
    >
      
      <List
        className="filelist"
        sx={{
          height: "100%", // 确保高度填满容器
          maxWidth: 600,
          bgcolor: "#000",
          color: "#F5F5F5",
          borderRadius: 2,
          padding: 2,
          overflow: "visible", // 确保内容可见
          "&::-webkit-scrollbar": {
            width: "8px",
          },
          "&::-webkit-scrollbar-thumb": {
            backgroundColor: "#2A2A2A", // 滚动条的颜色
            borderRadius: "4px",
          },
          "&::-webkit-scrollbar-thumb:hover": {
            backgroundColor: "#4A4A4A", // 鼠标悬停时滚动条的颜色
          },
          "&::-webkit-scrollbar-track": {
            backgroundColor: "#3A3A3A", // 滚动条轨道颜色
          },
        }}
      >
        {/* Addaxis Logo at the Top */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            marginBottom: '1rem',
          }}
        >
          <img
            src="./addaxis.webp"
            alt="AddAxis Logo"
            style={{
              maxWidth: '200px',
              height: 'auto',
              transform: 'scale(0.7)', // Scale the logo to 80%
            }}
          />
        </div>

        {/* Confirmation Dialog */}
        <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
          <DialogTitle>Delete Confirmation</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete{" "}
              <strong>{deleteTarget.name}</strong>?
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)} color="primary">
              Cancel
            </Button>
            <Button onClick={confirmDelete} color="error" autoFocus>
              Delete
            </Button>
          </DialogActions>
        </Dialog>

        {/* Company Profiles Section */}
        <ListSubheader
          disableSticky
          sx={{
            bgcolor: "transparent",
            color: "#F5F5F5",
            fontSize: "1.2rem",
            fontWeight: "bold",
            borderBottom: "1px solid #333",
            marginBottom: 1,
          }}
        >
          Company Profiles
        </ListSubheader>
        {companyProfiles.map((profile) => (
          <ListItem
            key={profile.id}
            sx={{
              bgcolor: "#333",
              borderRadius: 1,
              marginBottom: 1,
              transition: "background-color 0.2s ease",
              "&:hover": { bgcolor: "#444" },
            }}
            secondaryAction={
              <IconButton
                edge="end"
                onClick={() => handleDelete("profile", "" , profile.name)}
                sx={{
                  bgcolor: "#383838",
                  color: "#F5F5F5",
                  "&:hover": { bgcolor: "#555" },
                }}
              >
                <DeleteForeverIcon fontSize="small" />
              </IconButton>
            }
          >
            <ListItemText primary={profile.name} />
          </ListItem>
        ))}
        <ListItemButton
          onClick={triggerFileInput}
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            bgcolor: "#333",
            borderRadius: 3,
            marginBottom: 1,
            border: "2px dashed #6A6A6A",
            transition: "background-color 0.2s ease",
            "&:hover": { bgcolor: "#444" },
            gap: 1,
          }}
        >
          <ListItemText
            primary="Upload Profile File"
            sx={{
              textAlign: "center",
              flex: "none",
            }}
          />
          <FileUploadIcon fontSize="small" />
          <input
            type="file"
            ref={fileInputRef}
            onChange={addCompanyProfile}
            style={{ display: "none" }}
          />
        </ListItemButton>

        {/* Projects Section */}
        <ListSubheader
          disableSticky
          sx={{
            bgcolor: "transparent",
            color: "#F5F5F5",
            fontSize: "1.2rem",
            fontWeight: "bold",
            borderBottom: "1px solid #333",
            marginTop: 2,
            marginBottom: 1,
          }}
        >
          Projects
        </ListSubheader>
        {projects.map((project) => (
          <Fragment key={project.id}>
                  
        <ListItemButton
          sx={{
            marginBottom: 1,
            bgcolor: "#333",
            borderRadius: 1,
            transition: "background-color 0.2s ease",
            "&:hover": { bgcolor: "#444" },
          }}
          onClick={() => toggleProjectOpen(project.id)}
        >
          {openProjects[project.id] ? (
            <ExpandLess
              sx={{ marginRight: 1 }} // 添加右边距
            />
          ) : (
            <ExpandMore
              sx={{ marginRight: 1 }} // 添加右边距
            />
          )}
          <ListItemText primary={project.name} />
          <IconButton
            edge="end"
            onClick={() => handleDelete("project", project.name, project.name)}
            sx={{
              bgcolor: "#383838",
              color: "#F5F5F5",
              "&:hover": { bgcolor: "#555" },
            }}
          >
            <DeleteForeverIcon fontSize="small"/>
          </IconButton>
        </ListItemButton>


            {/* Collapse Section */}
            <Collapse
              in={openProjects[project.id]}
              timeout="auto"
              unmountOnExit
              sx={{
                bgcolor: "#222",
                borderRadius: 1,
                paddingBottom: openProjects[project.id] ? 2 : 0, // 动态调整填充
                marginBottom: 2,
              }}
            >
              <List
                component="div"
                disablePadding
                sx={{
                  paddingLeft: 4, // 左侧缩进
                }}
              >
                {project.files.map((file) => (
                  <ListItem
                    key={file.id}
                    sx={{
                      pl: 4,
                      bgcolor: "#333",
                      borderRadius: 1,
                      marginBottom: 1,
                      transition: "background-color 0.2s ease",
                      "&:hover": { bgcolor: "#444" },
                    }}
                    secondaryAction={
                      <IconButton
                        edge="end"
                        onClick={() => handleDelete("file", project.name, file.name)}
                        sx={{
                          bgcolor: "##383838",
                          color: "#F5F5F5",
                          "&:hover": { bgcolor: "#555" },
                        }}
                      >
                        <DeleteForeverIcon fontSize="small" />
                      </IconButton>
                    }
                  >
                    <ListItemText primary={file.name} />
                  </ListItem>
                ))}
                <ListItemButton
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    pl: 4,
                    bgcolor: "#333",
                    borderRadius: 3,
                    border: "2px dashed #6A6A6A", // 添加虚线边框
                    transition: "background-color 0.2s ease",
                    "&:hover": { bgcolor: "#444" },
                    gap: 1, // 图标和文字之间的间距
                  }}
                  onClick={() =>
                    document.getElementById(`fileInput-${project.id}`).click()
                  }
                >
                  <ListItemText
                    primary="Upload Project File"
                    sx={{
                      textAlign: "center",
                      flex: "none",
                    }}
                  />
                  <FileUploadIcon fontSize="small"/>
                  <input
                    type="file"
                    id={`fileInput-${project.id}`}
                    style={{ display: "none" }}
                    onChange={(e) => addFile(project.name, e.target.files[0])}
                  />
                </ListItemButton>
              </List>
            </Collapse>
          </Fragment>
        ))}
        <ListItemButton
          // onClick={addProject}
          onClick={handleDialogOpen}
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            bgcolor: "#333",
            borderRadius: 3,
            border: "2px dashed #6A6A6A", // 添加虚线边框
            transition: "background-color 0.2s ease",
            "&:hover": { bgcolor: "#444" },
            gap: 1, // 图标和文字之间的间距
          }}
        >
          <ListItemText
            primary="Add New Project"
            sx={{
              textAlign: "center",
              flex: "none",
            }}
          />
          <AddIcon fontSize="small"/>
        </ListItemButton>
      </List>

       {/* Dialog for creating a new project */}
       <Dialog
          open={dialogOpen}
          onClose={handleDialogClose}
          PaperProps={{
            sx: {
              backgroundColor: '#3A3A3A', // 背景颜色
              color: 'white', // 字体颜色
            },
          }}
        >
          <DialogTitle sx={{ color: 'white' }}>Add New Project</DialogTitle>
          <DialogContent>
            <DialogContentText sx={{ color: 'white' }}>
              Please enter the name of the new project.
            </DialogContentText>
            <TextField
              autoFocus
              margin="dense"
              label="Project Name"
              type="text"
              fullWidth
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              InputLabelProps={{
                style: { color: 'white' }, // Label颜色
              }}
              InputProps={{
                style: {
                  color: 'white', // 输入框字体颜色
                  backgroundColor: '#4A4A4A', // 输入框背景颜色
                },
              }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDialogClose} sx={{ color: 'white' }}>
              Cancel
            </Button>
            <Button onClick={addProject} sx={{ color: 'white' }}>
              Add
            </Button>
          </DialogActions>
        </Dialog>


        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbarOpen}
          autoHideDuration={1500} // Automatically close after 3 seconds
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: "top", horizontal: "center" }} // Snackbar position
        >
          <Alert
            onClose={handleSnackbarClose}
            severity={snackbarSeverity} // Dynamic severity
            sx={{ 
              width: "100%",
              fontWeight: "bold", // 设置字体加粗
              fontSize: "1rem",  // 可选：调整字体大小
            }}
          >
            {snackbarMessage}
          </Alert>
        </Snackbar>
    </div>

  );
};

export default FileList;
