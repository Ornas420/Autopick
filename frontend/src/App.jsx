import { Route, Routes, Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import Register from "./Register";
import Login from "./Login";
import EditUser from "./EditUser";
import Admin from "./Admin";
import Questionnaire from "./Questionnaire";
import Recommendation from "./Recommendation";
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsLoggedIn(true);
    } else {
      if (location.pathname !== "/register") {
        navigate("/login");
      }
    }
  }, [navigate, location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    navigate("/login");
  };

  const isOnQuizPage = location.pathname.includes("questionnaire") || location.pathname.includes("recommendation");

  return (
    <>
      {!isLoggedIn && (
        <nav>
          <Link to="/register">Register</Link>
          <Link to="/login">Login</Link>
        </nav>
      )}

      {isLoggedIn && !isOnQuizPage && (
        <>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>

          {location.pathname !== "/edit-user" && (
            <button className="edit-user-btn top-left" onClick={() => navigate("/edit-user")}>Edit User Info</button>
          )}

          {location.pathname !== "/admin" && (
            <button
              className="audit-logs-btn top-left"
              style={{ left: 150 }}
              onClick={() => navigate("/admin")}
            >
              Audit Logs
            </button>
          )}
        </>
      )}

      <Routes>
        <Route path="/" element={<Home isLoggedIn={isLoggedIn} navigate={navigate} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login onLogin={() => setIsLoggedIn(true)} />} />
        <Route path="/edit-user" element={<EditUser />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/questionnaire" element={<Questionnaire />} />
        <Route path="/recommendation" element={<Recommendation />} />
      </Routes>
    </>
  );
}

const Home = ({ isLoggedIn, navigate }) => (
  <div className="home-container">
    <div className="welcome-box">
      <h1>Welcome to Autopick!</h1>
      {isLoggedIn && (
        <button className="quiz-btn" onClick={() => navigate("/questionnaire")}>Take Car Quiz</button>
      )}
    </div>
  </div>
);

export default App;