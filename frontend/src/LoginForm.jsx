// src/LoginForm.jsx
import React, { useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post("http://localhost:8000/login", {
        username,
        password,
      });
      // Save user data to localStorage
      localStorage.setItem("username", response.data.username);
      localStorage.setItem("userId", response.data.user_id);
      localStorage.setItem("realUserId", response.data.real_user_id);
      localStorage.setItem("syntheticUserId", response.data.synthetic_user_id);
      localStorage.setItem("isSynthetic", response.data.is_synthetic);
      // Redirect to home
      navigate("/home");
    } catch (error) {
      setMessage("Login failed: " + (error.response?.data?.detail || "Unknown error"));
    }
  };

  return (
    <div style={styles.container}>
      <h2>Login</h2>
      <form onSubmit={handleLogin} style={styles.form}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={styles.input}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
        />
        <button type="submit" style={styles.button}>Login</button>
      </form>
      <p>
        Don't have an account? <Link to="/register">Register here</Link>
      </p>
      {message && <p style={styles.errorMessage}>{message}</p>}
    </div>
  );
}

const styles = {
  container: {
    margin: "200px auto",
    padding: 20,
    maxWidth: 300,
    textAlign: "center",
    border: "1px solid #ccc",
    borderRadius: 10,
    backgroundColor: "#fff",
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  input: {
    padding: 8,
    fontSize: 16,
    border: "1px solid #ddd",
    borderRadius: 5,
  },
  button: {
    padding: 10,
    backgroundColor: "#007bff",
    color: "#fff",
    border: "none",
    borderRadius: 5,
    cursor: "pointer",
    fontSize: 16,
    fontWeight: "bold",
  },
  errorMessage: {
    color: "#dc3545",
    marginTop: 10,
  },
};

export default LoginForm;
