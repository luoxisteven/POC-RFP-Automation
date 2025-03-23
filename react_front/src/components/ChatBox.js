import React, { useState } from "react";
import {
  Box,
  Typography,
  IconButton,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Button,
} from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import InfoIcon from "@mui/icons-material/Info";

const ChatBox = ({ messages }) => {
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const [currentContext, setCurrentContext] = useState({});

  const handleCopy = (text) => {
    // 去掉 "Total Response Time" 部分
    const processedText = text.replace(
      /\n\n <strong>Total Response Time:<\/strong> \d+ seconds/, // 匹配带有 "Total Response Time" 的文本
      ""
    );
  
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard
        .writeText(processedText)
        .then(() => {
          setSnackbarMessage("Message copied to clipboard!");
          setSnackbarSeverity("success");
          setSnackbarOpen(true);
        })
        .catch((err) => {
          console.error("Clipboard API failed: ", err);
          fallbackCopy(processedText);
        });
    } else {
      fallbackCopy(processedText);
    }
  };
  
  const fallbackCopy = (text) => {
    try {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();

      const success = document.execCommand("copy");
      document.body.removeChild(textarea);

      if (success) {
        setSnackbarMessage("Message copied to clipboard!");
        setSnackbarSeverity("success");
      } else {
        setSnackbarMessage("Failed to copy message.");
        setSnackbarSeverity("error");
      }
      setSnackbarOpen(true);
    } catch (err) {
      console.error("Fallback copy failed: ", err);
      setSnackbarMessage("Clipboard not supported.");
      setSnackbarSeverity("error");
      setSnackbarOpen(true);
    }
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbarOpen(false);
  };

  const formatMessage = (text) => {
    return text.replace(/\n/g, "<br>");
  };

  const handleOpenDialog = (context) => {
    setCurrentContext(context);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const formatContext = (text) => {
    if (!text) return "No data available";
    return text.replace(/\n/g, "<br>");
  };

  return (
    <Box
      sx={{
        flexGrow: 1,
        overflowY: "auto",
        marginBottom: 2,
        backgroundColor: "#3A3A3A",
        padding: 2,
        borderRadius: 1,
        fontFamily: "'Roboto', sans-serif",
        "&::-webkit-scrollbar": {
          width: "8px",
        },
        "&::-webkit-scrollbar-thumb": {
          backgroundColor: "#2A2A2A",
          borderRadius: "4px",
        },
        "&::-webkit-scrollbar-thumb:hover": {
          backgroundColor: "#4A4A4A",
        },
        "&::-webkit-scrollbar-track": {
          backgroundColor: "#3A3A3A",
        },
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              alignSelf: message.sender === "user" ? "flex-end" : "flex-start",
              backgroundColor: "#4A4A4A",
              padding: 2,
              borderRadius: 1,
              maxWidth: "70%",
              color: "#F5F5F5",
              wordBreak: "break-word",
              fontFamily: "'Roboto', sans-serif",
              boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.2)",
              position: "relative",
            }}
          >
            <Typography
              variant="body1"
              sx={{
                color: "#F5F5F5",
                wordBreak: "break-word",
                lineHeight: 1.5,
                fontSize: "0.9rem",
                letterSpacing: "0.02em",
              }}
              dangerouslySetInnerHTML={{
                __html: formatMessage(message.text),
              }}
            />
            {message.sender === "bot" && (
              <>
               <Box
                  sx={{
                    position: "absolute",
                    bottom: 8,
                    right: 8,
                    display: "flex",
                    gap: 1, // 按钮之间的间距设置为1（8px）
                  }}
                >
                  <IconButton
                    size="small"
                    onClick={() =>
                      handleOpenDialog({
                        query: message.query,
                        project_name: message.project_name,
                        rfp_local_context: message.rfp_local_context,
                        company_local_context: message.company_local_context,
                        rfp_general_context: message.rfp_general_context,
                        company_general_context: message.company_general_context,
                      })
                    }
                    sx={{
                      color: "#F5F5F5",
                      backgroundColor: "#5A5A5A",
                      padding: "4px 8px",
                      borderRadius: "8px",
                      boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.2)",
                      display: "flex",
                      alignItems: "center",
                      gap: 0.5, // 图标与文字间距
                      "&:hover": {
                        backgroundColor: "#6A6A6A",
                      },
                    }}
                  >
                    <InfoIcon fontSize="small" />
                    {/* <Typography
                      variant="caption"
                      sx={{
                        fontSize: "0.75rem",
                        color: "#F5F5F5",
                        fontWeight: "bold",
                      }}
                    >
                      context
                    </Typography> */}
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(message.text)}
                    sx={{
                      color: "#F5F5F5",
                      backgroundColor: "#5A5A5A",
                      padding: "4px 8px",
                      borderRadius: "8px",
                      boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.2)",
                      display: "flex",
                      alignItems: "center",
                      gap: 0.5, // 图标与文字间距
                      "&:hover": {
                        backgroundColor: "#6A6A6A",
                      },
                    }}
                  >
                    <ContentCopyIcon fontSize="small" />
                    {/* <Typography
                      variant="caption"
                      sx={{
                        fontSize: "0.75rem",
                        color: "#F5F5F5",
                        fontWeight: "bold",
                      }}
                    >
                      copy
                    </Typography> */}
                  </IconButton>
                </Box>

              </>
            )}
          </Box>
        ))}
      </Box>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={2000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbarSeverity}
          sx={{
            width: "100%",
            fontWeight: "bold",
            fontSize: "1rem",
          }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>

      {/* Dialog for context */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#3A3A3A', // 深色背景
            color: 'white', // 白色字体
          },
        }}
      >
        <DialogTitle sx={{ color: 'white' }}>Query Context</DialogTitle>
        <DialogContent>
          {/* 添加 Query 信息 */}
          <Typography
            variant="subtitle1"
            sx={{
              marginBottom: 1, // 调整 Query 与 Project 的间距
              fontStyle: "italic",
              color: "#ccc", // 浅灰色字体
            }}
          >
            Query: {currentContext.query || ""}
          </Typography>
          {/* 添加 Project 信息 */}
          <Typography
            variant="subtitle1"
            sx={{
              marginBottom: 2, // 为 Project 与 Tabs 之间提供间距
              fontStyle: "italic",
              color: "#ccc", // 浅灰色字体
            }}
          >
            Project: {currentContext.project_name}
          </Typography>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            variant="fullWidth"
            TabIndicatorProps={{
              style: { backgroundColor: 'white' }, // 标签指示器颜色
            }}
            sx={{
              '& .MuiTab-root': {
                color: 'white', // 标签默认字体颜色
                // border: '1px solid #666', // 添加边框
                borderBottom: '1px solid #666',
                borderRadius: '4px', // 边框圆角
                margin: '0 4px', // 每个 Tab 之间增加间距
              },
              '& .Mui-selected': {
                color: 'white', // 选中标签的字体颜色
                backgroundColor: '#555', // 选中标签的背景颜色
              },
            }}
          >
            <Tab label="RFP Local Context" />
            <Tab label="Company Local Context" />
            <Tab label="RFP General Context" />
            <Tab label="Company General Context" />
          </Tabs>
          <Box
            sx={{
              marginTop: 2,
              maxHeight: "400px",
              overflowY: "auto",
              padding: 2,
              backgroundColor: "#4A4A4A", // 内容框背景色
              borderRadius: "8px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.5)", // 阴影加深
              "&::-webkit-scrollbar": {
                width: "8px", // 滚动条宽度
              },
              "&::-webkit-scrollbar-thumb": {
                backgroundColor: "#2A2A2A", // 滚动条颜色
                borderRadius: "4px", // 滚动条圆角
              },
              "&::-webkit-scrollbar-thumb:hover": {
                backgroundColor: "#4A4A4A", // 滚动条悬停颜色
              },
              "&::-webkit-scrollbar-track": {
                backgroundColor: "#3A3A3A", // 滚动条轨道颜色
              },
            }}
          >
            {selectedTab === 0 && (
              <Typography
                dangerouslySetInnerHTML={{
                  __html: formatContext(currentContext.rfp_local_context),
                }}
                sx={{ color: 'white' }} // 内容字体颜色
              />
            )}
            {selectedTab === 1 && (
              <Typography
                dangerouslySetInnerHTML={{
                  __html: formatContext(currentContext.company_local_context),
                }}
                sx={{ color: 'white' }}
              />
            )}
            {selectedTab === 2 && (
              <Typography
                dangerouslySetInnerHTML={{
                  __html: formatContext(currentContext.rfp_general_context),
                }}
                sx={{ color: 'white' }}
              />
            )}
            {selectedTab === 3 && (
              <Typography
                dangerouslySetInnerHTML={{
                  __html: formatContext(currentContext.company_general_context),
                }}
                sx={{ color: 'white' }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} sx={{ color: 'white' }}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatBox;
