
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
      const response = await axios.put("https://127.0.0.1:5000/update_user", {
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
        navigate("/");
      }
    } catch (error) {
      setMessage(error.response?.data?.error || "An error occurred");
    }
  };

  const handleDelete = async () => {
    const confirm = window.confirm("Are you sure you want to delete your account?");
    if (!confirm) return;

    try {
      const token = localStorage.getItem("token");
      const response = await axios.delete("https://127.0.0.1:5000/delete_account", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      setMessage(response.data.message);
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      navigate("/");
    } catch (error) {
      setMessage(error.response?.data?.error || "Error deleting account");
    }
  };

  return (
    <div className="center-screen">
      <div className="form-container">
        <h2>Edit Account</h2>
        <form onSubmit={handleUpdate}>
          <input
            type="text"
            placeholder="New username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="input-field"
          />
          <input
            type="password"
            placeholder="New password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-field"
          />
          <button type="submit" className="btn">Update</button>
        </form>

        <button onClick={handleDelete} className="btn danger" style={{ marginTop: '1rem' }}>
          Delete Account
        </button>

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );

}

export default EditUser;
