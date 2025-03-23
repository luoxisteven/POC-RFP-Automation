import React, { useState, useRef } from "react";
import request from "../utils/request";
import SendIcon from "@mui/icons-material/Send";
import CancelScheduleSendIcon from '@mui/icons-material/CancelScheduleSend';
import {
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  CircularProgress,
  Box,
} from "@mui/material";

const ChatInput = ({ projects, addMessage }) => {
  const [userInput, setUserInput] = useState("");
  const [selectedProject, setSelectedProject] = useState("");
  const [selectedMode, setSelectedMode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [timer, setTimer] = useState(0);
  const timerRef = useRef(0);
  const intervalId = useRef(null);

  const handleSend = async () => {
    if (selectedProject && (selectedMode === "Question Extraction" || userInput.trim())) {
      const formData = new FormData();
      formData.append("project_name", selectedProject);
  
      if (selectedMode !== "Question Extraction") {
        formData.append("query", userInput);
      }
  
      if (selectedMode === "Question Extraction") {
        addMessage({ sender: "user", text: "Question Extraction\n(" + selectedProject + ")" });
      } else {
        addMessage({ sender: "user", text: userInput + "\n(" + selectedProject + ")" });
      }
  
      setUserInput("");
      setIsLoading(true);
      startTimer();
  
      let apiPath;
      switch (selectedMode) {
        case "Question Extraction":
          apiPath = "/get_question/";
          break;
        case "Simple Answer":
          apiPath = "/get_simple_answer_verbose/";
          break;
        case "Detailed Answer":
          apiPath = "/get_detailed_answer_verbose/";
          break;
        default:
          console.warn("Invalid mode selected");
          return;
      }
  
      try {
        const response = await request.post(apiPath, formData);
        stopTimer();
        const finalTime = timerRef.current;
  
        let answer;
        if (selectedMode === "Question Extraction") {
          answer = 
            response.answer +
              "\n\n <strong>Total Response Time:</strong> " +
              finalTime +
              " seconds";
        } else {
          answer =
            response.answer.answer +
            "\n\n <strong>Total Response Time:</strong> " +
            finalTime +
            " seconds";
        }
  
        const rfp_local_context = response.answer.rfp_local_context;
        const company_local_context = response.answer.company_local_context;
        const rfp_general_context = response.answer.rfp_general_context;
        const company_general_context = response.answer.company_general_context;
  
        addMessage({
          sender: "bot",
          project_name: selectedProject,
          query: userInput,
          text: answer,
          rfp_local_context: rfp_local_context,
          company_local_context: company_local_context,
          rfp_general_context: rfp_general_context,
          company_general_context,
        });
      } catch (error) {
        console.error("Error fetching answer:", error);
        addMessage({ sender: "bot", text: "Error retrieving answer. Please try again later." });
      } finally {
        setIsLoading(false);
      }
    }
  };
  

  const startTimer = () => {
    setTimer(0);
    timerRef.current = 0;
    intervalId.current = setInterval(() => {
      setTimer((prevTimer) => {
        timerRef.current = prevTimer + 1;
        return prevTimer + 1;
      });
    }, 1000);
  };

  const stopTimer = () => {
    clearInterval(intervalId.current);
    intervalId.current = null;
  };

  return (
    <Box
      sx={{
        p: 2,
        display: "flex",
        flexDirection: "column",
        gap: 2,
        backgroundColor: "#3A3A3A",
        borderRadius: "5px", // Rounded borders
        borderTop: "1px solid #dddddd", // Top separator line
        fontFamily: "'Roboto', sans-serif", // Apply the Roboto font globally to the component
      }}
    >
      {/* Dropdowns and Loading */}
      <Box
        sx={{
          display: "flex",
          gap: 2,
          alignItems: "center",
        }}
      >
        {/* Project Selector */}
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel
            id="project-select-label"
            sx={{
              color: "#F5F5F5", // White font
              fontSize: "0.9rem", // Adjust font size
              fontFamily: "'Roboto', sans-serif", // Apply Roboto font
            }}
          >
            Select a project
          </InputLabel>
          <Select
            labelId="project-select-label"
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            label="Choose Project"
            sx={{
              backgroundColor: "#4A4A4A", // Dark gray background
              color: "#F5F5F5", // White font
              fontSize: "0.9rem", // Adjust font size
              fontFamily: "'Roboto', sans-serif", // Apply Roboto font
            }}
          >
            <MenuItem value="" disabled>
              Project
            </MenuItem>
            {projects.map((project, index) => (
              <MenuItem
                key={index}
                value={project.name}
                sx={{ fontFamily: "'Roboto', sans-serif" }} // Apply Roboto font to dropdown items
              >
                {project.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Mode Selector */}
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel
            id="mode-select-label"
            sx={{
              color: "#F5F5F5", // White font
              fontSize: "0.9rem", // Adjust font size
              fontFamily: "'Roboto', sans-serif", // Apply Roboto font
            }}
          >
            Select a mode
          </InputLabel>
          <Select
            labelId="mode-select-label"
            value={selectedMode}
            onChange={(e) => setSelectedMode(e.target.value)}
            label="Mode"
            sx={{
              backgroundColor: "#4A4A4A", // Dark gray background
              color: "#F5F5F5", // White font
              fontSize: "0.9rem", // Adjust font size
              fontFamily: "'Roboto', sans-serif", // Apply Roboto font
            }}
          >
            <MenuItem value="" disabled>
              Mode
            </MenuItem>
            <MenuItem value="Question Extraction">Question Extraction (0 to 5 min)</MenuItem>
            <MenuItem value="Simple Answer">Simple Answer (3 to 10 min)</MenuItem>
            <MenuItem value="Detailed Answer">Detailed Answer (5 to 20 min)</MenuItem>
          </Select>
        </FormControl>

        {/* Loading Indicator */}
        {isLoading && (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1,
              color: "#F5F5F5", // White font
              minWidth: 100, // Reserve space for loading icon and text
              fontFamily: "'Roboto', sans-serif", // Apply Roboto font
            }}
          >
            <CircularProgress size={20} />
            <span>{timer}s</span>
          </Box>
        )}
      </Box>

      {/* Input Field */}
      <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
        <TextField
          fullWidth
          placeholder="Please enter a query..."
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyUp={(e) => e.key === "Enter" && handleSend()}
          variant="outlined"
          sx={{
            backgroundColor: "#4A4A4A", // Dark gray background
            color: "#F5F5F5", // White font
            borderRadius: "5px", // Rounded borders
            fontFamily: "'Roboto', sans-serif", // Apply Roboto font
          }}
          InputProps={{
            style: { color: "#F5F5F5", fontFamily: "'Roboto', sans-serif" }, // White input text and Roboto font
          }}
        />
        <Button
          onClick={handleSend}
          variant="contained"
          sx={{
            backgroundColor: isLoading || !selectedMode || !selectedProject ? "#1A1A1A" : "#5A5A5A", // Change background color based on disabled state
            color: "#F5F5F5", // Icon color remains white
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            "&:hover": {
              backgroundColor: isLoading || !selectedMode || !selectedProject ? "#1A1A1A" : "#7A7A7A", // Keep hover effect for enabled state
            },
            borderRadius: "5px",
            width: "50px", // Adjust width
            height: "50px", // Adjust height
            fontFamily: "'Roboto', sans-serif", // Apply Roboto font to the button
          }}
          disabled={isLoading || !selectedMode || !selectedProject}
        >
          {isLoading || !selectedMode || !selectedProject ? (
            <CancelScheduleSendIcon sx={{ color: "#E0E0E0" }} />
          ) : (
            <SendIcon />
          )}
        </Button>
      </Box>
    </Box>
  );
};

export default ChatInput;
