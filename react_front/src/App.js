import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import FileList from './components/FileList';
import ChatBox from './components/ChatBox';
import ChatInput from './components/ChatInput';
import Login from './components/Login';
import './App.css';

const App = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'sys',
      text: '<strong>Guidelines:</strong> \n1) Use the menu on the left to add or remove projects and files;\n2) Choose your project and mode from the dropdown lists below;\n3) Submit a query related to the selected project.\n\n<strong>A simple answer typically takes 3 to 10 minutes, while a detailed answer may take 5 to 20 minutes.\n\nThank you for your patience! It might take a little longer than expected.</strong>'
    }
  ]);
  const [projects, setProjects] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const updateProjects = (updatedProjects) => {
    setProjects(updatedProjects);
  };

  const addMessageToChatBox = (message) => {
    setMessages((prevMessages) => {
      const updatedMessages = [...prevMessages, message];
      console.log(updatedMessages); // 在这里可以看到更新的数组
      return updatedMessages;
    });
  };

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  return (
    <Router>
      <Routes>
        {/* 如果用户未登录，自动跳转到 /login */}
        <Route
          path="/login"
          element={<Login onLoginSuccess={handleLoginSuccess} />}
        />
        <Route
          path="/"
          element={
            <div className="app-container">
                <FileList updateProjects={updateProjects} />
                <div className="chat-container">
                  <ChatBox messages={messages} />
                  <ChatInput projects={projects} addMessage={addMessageToChatBox} />
                </div>
              </div>
            // isAuthenticated ? (
            //   <div className="app-container">
            //     <FileList updateProjects={updateProjects} />ß
            //     <div className="chat-container">
            //       <ChatBox messages={messages} />
            //       <ChatInput projects={projects} addMessage={addMessageToChatBox} />
            //     </div>
            //   </div>
            // ) : (
            //   <Navigate to="/login" replace />
            // )
          }
        />
      </Routes>
    </Router>
  );
};

export default App;
