// utils/request.js (React version)
import axios from 'axios';

const request = axios.create({
  baseURL: 'http://13.236.191.152:8000',
  // baseURL: 'http://localhost:8000',
  timeout: 1800000,
});

// Request interceptor
request.interceptors.request.use(
  (config) => {
    // Check if data is an instance of FormData to avoid setting JSON Content-Type
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json;charset=utf-8';
    }

    // Optional: Add other headers like token if needed
    // config.headers['token'] = user.token;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
request.interceptors.response.use(
  (response) => {
    let res = response.data;
    if (response.config.responseType === 'blob') {
      return res;
    }
    if (typeof res === 'string') {
      res = res ? JSON.parse(res) : res;
    }
    return res;
  },
  (error) => {
    console.error('Error:', error); // For debug
    return Promise.reject(error);
  }
);

export default request;

// To use this request instance globally
// Import this in any component where you need to make HTTP requests:
// import request from '../utils/request';
// Example usage:
// request.get('/some-endpoint').then(response => { console.log(response); });
