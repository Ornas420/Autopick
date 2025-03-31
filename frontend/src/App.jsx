import { Route, Routes, Link, useNavigate, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import Register from "./Register";
import Login from "./Login";
import EditUser from "./EditUser";
import Admin from './Admin';
import "./App.css";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();
  const location = useLocation(); // Get the current path
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      setIsLoggedIn(true);
    } else {
      // ✅ Allow access to register page even when not logged in
      if (location.pathname !== "/register") {
        navigate("/login"); // Redirect if not logged in
      }
    }
  }, [navigate, location.pathname]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    navigate("/login");
  };

  return (
    <>
      {!isLoggedIn && (
        <nav>
          <Link to="/register">Register</Link>
          <Link to="/login">Login</Link>
        </nav>
      )}

      {isLoggedIn && (
        <>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>

          {location.pathname !== "/edit-user" && (
            <button className="edit-user-btn" onClick={() => navigate("/edit-user")}>
              Edit User Info
            </button>
          )}

          {location.pathname !== "/admin" && (
            <button
  className="audit-logs-btn"
  onClick={() => navigate("/admin")}
  style={{
    position: "absolute",
    top: 10,
    left: 130,
    backgroundColor: "green",
    color: "white",
    border: "none",
    padding: "8px 12px",
    borderRadius: "4px",
    cursor: "pointer",
    marginLeft: "30px" // 👈 space between buttons
  }}
>
  Audit Logs
</button>

          )}
        </>
      )}

      <Routes>
        <Route path="/" element={<Home isLoggedIn={isLoggedIn} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login onLogin={() => setIsLoggedIn(true)} />} />
        <Route path="/edit-user" element={<EditUser />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </>
  );
}

const Home = ({ isLoggedIn }) => (
  <div>
    <h1>Welcome to Autopick!</h1>
    <p>Please answer the following questions:</p>
    <ul>
      <li>Do you want a fuel-efficient car?</li>
      <li>Do you need cargo space?</li>
      <li>Will you be driving in snow?</li>
    </ul>
  </div>
);

export default App;
