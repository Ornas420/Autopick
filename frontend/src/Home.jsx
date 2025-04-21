import React from "react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const username = localStorage.getItem("username");
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <div className="page-wrapper">
      {/* Top Buttons */}
      <div className="top-buttons">
        <div className="left-buttons">
          <button className="btn" onClick={() => navigate("/edit-user")}>Edit User Info</button>
          <button className="btn" onClick={() => navigate("/admin")}>Audit Logs</button>
        </div>
        <div className="right-buttons">
          <button className="btn logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </div>

      {/* Centered Welcome Box */}
      <div className="home-container">
        <div className="welcome-box">
          <h1>Welcome to Autopick{username ? `, ${username}` : ""}!</h1>
          <button className="btn quiz-btn" onClick={() => navigate("/questionnaire")}>
            🚗 Take Car Quiz
          </button>
        </div>
      </div>
    </div>
  );
}
