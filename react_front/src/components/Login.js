import React, { useState } from "react";
import { TextField, Button, Box, Typography, Paper, Dialog, DialogTitle, DialogContent, DialogActions } from "@mui/material";
import { styled } from "@mui/material/styles";
import { useNavigate } from "react-router-dom";

const LoginBox = styled(Paper)({
  width: 350,
  padding: "20px 20px 60px", // 为底部按钮留出额外空间
  borderRadius: 10,
  textAlign: "center",
  position: "relative", // 让内部按钮可以相对于这个容器定位
});

const GradientBackground = styled(Box)({
  height: "100vh",
  backgroundImage: "linear-gradient(to bottom right, #FC466B, #3F5EFB)",
  overflow: "hidden",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  fontFamily: "'Roboto', sans-serif", // 添加字体
});

const LoginButtonContainer = styled(Box)({
  position: "absolute", // 绝对定位按钮
  bottom: 20, // 距离底部 20px
  right: 20, // 距离右侧 20px
  display: "flex", // 横向布局
  gap: 10, // 按钮之间的间距
});

const Login = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState({ username: "", password: "" });
  const [openDialog, setOpenDialog] = useState(false); // 控制弹出框的状态
  const [signUpData, setSignUpData] = useState({
    username: "",
    password: "",
    confirmPassword: "",
    email: "",
  });

  const handleLogin = () => {
    if (user.username === "admin" && user.password === "123456") {
      navigate("/");
    } else {
      alert("Incorrect username or password");
    }
  };
  
  const handleSignUp = () => {
    if (signUpData.password !== signUpData.confirmPassword) {
      alert("The passwords entered do not match");
      return;
    }
    // Simulate registration logic
    alert(`Registration successful!\nUsername: ${signUpData.username}\nEmail: ${signUpData.email}`);
    setOpenDialog(false); // Close the dialog box
  };

  return (
    <GradientBackground>
      <LoginBox elevation={5}>
        <Typography variant="h5" gutterBottom>
          Login
        </Typography>
        <Box component="form" noValidate autoComplete="off">
          <TextField
            fullWidth
            label="Username"
            variant="outlined"
            margin="normal"
            value={user.username}
            onChange={(e) => setUser({ ...user, username: e.target.value })}
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            variant="outlined"
            margin="normal"
            value={user.password}
            onChange={(e) => setUser({ ...user, password: e.target.value })}
          />
        </Box>
        {/* 放置按钮的容器 */}
        <LoginButtonContainer>
          <Button variant="outlined" color="secondary" onClick={() => setOpenDialog(true)}>
            Sign Up
          </Button>
          <Button variant="contained" color="primary" onClick={handleLogin}>
            Login
          </Button>
        </LoginButtonContainer>
      </LoginBox>

      {/* 注册弹出框 */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Sign Up</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Username"
            variant="outlined"
            margin="normal"
            value={signUpData.username}
            onChange={(e) => setSignUpData({ ...signUpData, username: e.target.value })}
          />
          <TextField
            fullWidth
            label="Password"
            type="password"
            variant="outlined"
            margin="normal"
            value={signUpData.password}
            onChange={(e) => setSignUpData({ ...signUpData, password: e.target.value })}
          />
          <TextField
            fullWidth
            label="Confirm Password"
            type="password"
            variant="outlined"
            margin="normal"
            value={signUpData.confirmPassword}
            onChange={(e) => setSignUpData({ ...signUpData, confirmPassword: e.target.value })}
          />
          <TextField
            fullWidth
            label="Email"
            type="email"
            variant="outlined"
            margin="normal"
            value={signUpData.email}
            onChange={(e) => setSignUpData({ ...signUpData, email: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleSignUp} color="primary" variant="contained">
            Register
          </Button>
        </DialogActions>
      </Dialog>
    </GradientBackground>
  );
};

export default Login;
