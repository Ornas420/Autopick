import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { useEffect } from "react";

// Page components
import Home from "./Home";
import Register from "./Register";
import Login from "./Login";
import EditUser from "./EditUser";
import Admin from "./Admin";
import Questionnaire from "./Questionnaire";
import Recommendation from "./Recommendation";

import "./App.css";

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const publicRoutes = ["/login", "/register"];

    if (!token && !publicRoutes.includes(location.pathname)) {
      navigate("/login");
    }
  }, [location.pathname, navigate]);

  return (
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/edit-user" element={<EditUser />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/questionnaire" element={<Questionnaire />} />
        <Route path="/recommendation" element={<Recommendation />} />
      </Routes>
    </>
  );
}

export default App;
