// // App.js
// import React, { useState } from 'react';
// import FileList from './components/FileList';
// import ChatBox from './components/ChatBox';
// import ChatInput from './components/ChatInput';
// import './App.css';

// const App = () => {
//   const [messages, setMessages] = useState([
//     {
//       sender: 'sys',
//       text: '<strong>Guidelines:</strong> \n1) Add or delete projects or files from the menu on the left;\n2) Select your project and mode from the dropdown lists below;\n3) Enter a query related to the selected project.\n\n<strong>Please be patient!\n\nA simple answer takes 3 to 10 minutes, while a detailed answer takes 5 to 15 minutes.</strong>'
//     }
//   ]);
//   const [projects, setProjects] = useState([]);

//   const updateProjects = (updatedProjects) => {
//     setProjects(updatedProjects);
//   };

//   const addMessageToChatBox = (message) => {
//     setMessages([...messages, message]);
//   };

//   return (
//     <div className="app-container">
//       <FileList updateProjects={updateProjects} />
//       <div className="chat-container">
//         <ChatBox messages={messages} />
//         <ChatInput projects={projects} addMessage={addMessageToChatBox} />
//       </div>
//     </div>
//   );
// };

// export default App;

// // FileList.js
// import React, { useState, useEffect, useRef, useCallback } from 'react';
// import request from '../utils/request';
// import '../App.css';

// const FileList = ({ updateProjects }) => {
//   const [companyProfiles, setCompanyProfiles] = useState([]);
//   const [projects, setProjects] = useState([]);
//   const fileInputRef = useRef(null);

//   const fetchData = useCallback(async () => {
//     try {
//       const data = await request.get('/get');

//       // Company profile
//       setCompanyProfiles(data.company_profiles.map((name, index) => ({
//         id: index + 1,
//         name
//       })));

//       // Project Data
//       const projectList = Object.keys(data.rfps).map((projectKey, index) => ({
//         id: index + 1,
//         name: projectKey,
//         files: data.rfps[projectKey].map((fileName, fileIndex) => ({
//           id: fileIndex + 1,
//           name: fileName
//         }))
//       }));
//       setProjects(projectList);
//       updateProjects(projectList);
//     } catch (error) {
//       console.error('Error fetching data:', error);
//     }
//   }, [updateProjects]);

//   useEffect(() => {
//     fetchData();
//   }, [fetchData]);

//   const triggerFileInput = () => {
//     fileInputRef.current.click();
//   };

//   const addCompanyProfile = async (event) => {
//     const file = event.target.files[0];
//     if (!file) return;
//     const formData = new FormData();
//     formData.append('file', file);

//     try {
//       const result = await request.post('/add_company_profile/', formData);

//       if (result.status === 'success') {
//         fetchData(); // Refresh data after successful upload
//       } else {
//         console.error('Failed to upload file:', result.message);
//       }
//     } catch (error) {
//       console.error('Error uploading file:', error);
//     } finally {
//       event.target.value = ''; // Reset file input
//     }
//   };

//   const deleteCompanyProfile = async (profileName) => {
//     try {
//       const result = await request.post('/del_company_profile/', {
//         file_name: profileName
//       });

//       if (result.status === 'success') {
//         fetchData(); // Refresh data to update the UI
//       } else {
//         console.error('Failed to delete file:', result.message);
//       }
//     } catch (error) {
//       console.error('Error deleting file:', error);
//     }
//   };

//   const addProject = async () => {
//     const projectName = prompt('Input your new project name');
//     if (!projectName) return;

//     try {
//       const result = await request.post('/add_project/', {
//         project_name: projectName
//       });

//       if (result.status === 'success') {
//         fetchData(); // Refresh data to update the UI
//       } else {
//         console.error('Failed to create project:', result.message);
//       }
//     } catch (error) {
//       console.error('Error creating project:', error);
//     }
//   };

//   const deleteProject = async (projectName) => {
//     try {
//       const result = await request.post('/del_project/', {
//         project_name: projectName
//       });

//       if (result.status === 'success') {
//         fetchData(); // Refresh data to update the UI
//       } else {
//         console.error('Failed to delete project:', result.message);
//       }
//     } catch (error) {
//       console.error('Error deleting project:', error);
//     }
//   };

//   const addFile = async (projectName, file) => {
//     const formData = new FormData();
//     formData.append('project_name', projectName);
//     formData.append('file', file);

//     try {
//       const result = await request.post('/add_project_file/', formData);

//       if (result.status === 'success') {
//         fetchData(); // Refresh data to update the UI
//       } else {
//         console.error('Failed to upload file:', result.message);
//       }
//     } catch (error) {
//       console.error('File upload error:', error);
//       alert('Error uploading file.');
//     }
//   };

//   const deleteFile = async (projectName, fileName) => {
//     try {
//       const result = await request.post('/del_project_file/', {
//         project_name: projectName,
//         file_name: fileName
//       });

//       if (result.status === 'success') {
//         fetchData(); // Refresh data to update the UI
//       } else {
//         console.error('Failed to delete file:', result.message);
//       }
//     } catch (error) {
//       console.error('Error deleting file:', error);
//     }
//   };

//   return (
//     <div className="filelist">
//       <div className="header company-header">
//         <h3>Company Profile</h3>
//         <button className="add-btn" onClick={triggerFileInput}>+</button>
//         <input type="file" ref={fileInputRef} onChange={addCompanyProfile} style={{ display: 'none' }} />
//       </div>
//       <ul>
//         {companyProfiles.map((profile) => (
//           <li key={profile.id} className="profile-item">
//             <div className="profile-header">
//               <span>{profile.name}</span>
//               <button className="delete-btn" onClick={() => deleteCompanyProfile(profile.name)}>-</button>
//             </div>
//           </li>
//         ))}
//       </ul>

//       <div className="header">
//         <h3>Projects</h3>
//         <button className="add-btn" onClick={addProject}>+</button>
//       </div>
//       <ul>
//         {projects.map((project) => (
//           <li key={project.id} className="project-item">
//             <div className="project-header">
//               <span>{project.name}</span>
//               <div className="button-group">
//                 <input type="file" onChange={(e) => addFile(project.name, e.target.files[0])} />
//                 <button className="delete-btn" onClick={() => deleteProject(project.name)}>-</button>
//               </div>
//             </div>
//             <ul className="file-list">
//               {project.files.map((file) => (
//                 <li key={file.id} className="file-item">
//                   <span>{file.name}</span>
//                   <button className="delete-btn" onClick={() => deleteFile(project.name, file.name)}>-</button>
//                 </li>
//               ))}
//             </ul>
//           </li>
//         ))}
//       </ul>
//     </div>
//   );
// };

// export default FileList;

// // ChatBox.js
// import React from 'react';
// import '../App.css';

// const ChatBox = ({ messages }) => {
//   const formatMessage = (text) => {
//     // Simple formatting for newlines and basic HTML tags
//     return text.replace(/\n/g, '<br>');
//   };

//   return (
//     <div className="chatbox">
//       <div className="messages">
//         {messages.map((message, index) => (
//           <div
//             key={index}
//             className={`message ${message.sender === 'user' ? 'user-message' : message.sender === 'bot' ? 'bot-message' : 'sys-message'}`}
//             dangerouslySetInnerHTML={{ __html: formatMessage(message.text) }}
//           ></div>
//         ))}
//       </div>
//     </div>
//   );
// };

// export default ChatBox;
