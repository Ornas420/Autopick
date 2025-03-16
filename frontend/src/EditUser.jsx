import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function EditUser() {
  const [username, setUsername] = useState(localStorage.getItem("username") || "");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("token");
      const response = await axios.put("http://127.0.0.1:5000/update_user", {
        username,
        password,
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setMessage(response.data.message);
      if (response.data.message === 'User information updated successfully') {
        localStorage.setItem("username", username);
        navigate("/"); // Redirect to home or any other page
      }
    } catch (error) {
      setMessage(error.response?.data?.error || "An error occurred");
    }
  };

  return (
    <div className="form-container">
      <h2>Edit User Information</h2>
      <form onSubmit={handleUpdate}>
        <input
          type="text"
          placeholder="New Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="input-field"
        />
        <input
          type="password"
          placeholder="New Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="input-field"
        />
        <button type="submit" className="btn">Confirm</button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default EditUser;