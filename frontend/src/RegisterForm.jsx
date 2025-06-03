// src/RegisterForm.jsx
import React, { useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";

function RegisterForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [dataSource, setDataSource] = useState("synthetic");
  const [realUserId, setRealUserId] = useState(0);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post("http://localhost:8000/register", {
        username,
        password,
        use_real_data: dataSource === "real",
        real_user_id: dataSource === "real" ? realUserId : null,
        synthetic_user_id: dataSource === "synthetic" ? Math.floor(Math.random() * 200) : null
      });

      setTimeout(() => navigate("/"), 300);
    } catch (error) {
      setMessage("Registration failed: " + (error.response?.data?.detail || "Unknown error"));
    }
  };

  return (
    <div style={styles.container}>
      <h2>Register</h2>
      <form onSubmit={handleRegister} style={styles.form}>
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
        
        <div style={styles.dataSourceContainer}>
          <h4 style={styles.sectionTitle}>Choose Data Source</h4>
          
          <div style={styles.radioGroup}>
            <label style={styles.radioLabel}>
              <input
                type="radio"
                value="synthetic"
                checked={dataSource === "synthetic"}
                onChange={(e) => setDataSource(e.target.value)}
                style={styles.radio}
              />
              <div style={styles.radioContent}>
                <div style={styles.radioTitle}>Synthetic Data</div>
                <div style={styles.radioDescription}>
                  Synthetic data simulating real patterns, will be randomly assigned
                </div>
              </div>
            </label>

            <label style={styles.radioLabel}>
              <input
                type="radio"
                value="real"
                checked={dataSource === "real"}
                onChange={(e) => setDataSource(e.target.value)}
                style={styles.radio}
              />
              <div style={styles.radioContent}>
                <div style={styles.radioTitle}>Real Data</div>
                <div style={styles.radioDescription}>
                  Data from real users. Choose a specific user or get a random one
                </div>
              </div>
            </label>
          </div>

          {dataSource === "real" && (
            <div style={styles.realDataOptions}>
              <select
                value={realUserId}
                onChange={(e) => setRealUserId(Number(e.target.value))}
                style={styles.select}
              >
                <option value={0}>Random User</option>
                {[...Array(25)].map((_, i) => (
                  <option key={i + 1} value={i + 1}>
                    Real User #{i + 1}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <button type="submit" style={styles.button}>Register</button>
      </form>
      <p>
        Already have an account? <Link to="/">Login</Link>
      </p>
      {message && <p style={styles.errorMessage}>{message}</p>}
    </div>
  );
}

const styles = {
  container: {
    margin: "100px auto",
    padding: 20,
    maxWidth: 500,
    textAlign: "center",
    border: "1px solid #ccc",
    borderRadius: 10,
    backgroundColor: "#fff",
    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: 15,
  },
  input: {
    padding: 8,
    fontSize: 16,
    border: "1px solid #ddd",
    borderRadius: 5,
  },
  button: {
    padding: 12,
    backgroundColor: "#28a745",
    color: "#fff",
    border: "none",
    borderRadius: 5,
    cursor: "pointer",
    fontSize: 16,
    fontWeight: "bold",
    marginTop: 10,
  },
  dataSourceContainer: {
    textAlign: "left",
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 15,
    marginTop: 15,
    color: "#333",
  },
  radioGroup: {
    display: "flex",
    flexDirection: "column",
    gap: 15,
  },
  radioLabel: {
    display: "flex",
    alignItems: "flex-start",
    padding: 10,
    border: "1px solid #ddd",
    borderRadius: 5,
    cursor: "pointer",
    transition: "all 0.2s",
  },
  radio: {
    marginTop: 3,
    marginRight: 10,
  },
  radioContent: {
    flex: 1,
  },
  radioTitle: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 5,
    color: "#333",
  },
  radioDescription: {
    fontSize: 14,
    color: "#666",
  },
  realDataOptions: {
    marginTop: 15,
    padding: 10,
    backgroundColor: "transparent",
    borderRadius: 5,
  },
  select: {
    width: "100%",
    padding: 8,
    fontSize: 14,
    border: "none",
    borderRadius: 4,
    backgroundColor: "transparent",
  },
  errorMessage: {
    color: "#dc3545",
    marginTop: 10,
  },
};

export default RegisterForm;
