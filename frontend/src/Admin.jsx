import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Admin() {
  const [logs, setLogs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');

    if (!username || !token) {
      console.error("Missing token or username.");
      return;
    }

    fetch(`http://localhost:5000/api/logs/${username}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(res => res.json())
      .then(data => setLogs(data))
      .catch(err => console.error('Failed to fetch logs:', err));
  }, []);

  return (
    <div className="audit-logs-container">
      {/* Return Button */}
      <button
        onClick={() => navigate('/')}
        style={{
          position: 'absolute',
          top: '10px',
          left: '10px',
          backgroundColor: '#4B5563',
          color: 'white',
          fontSize: '18px',
          fontWeight: 'bold',
          padding: '12px 20px',
          borderRadius: '6px',
          border: 'none',
          cursor: 'pointer',
        }}
      >
        ← Return Home
      </button>

      {/* Logs Section */}
      <h1 className="text-3xl font-bold mb-4">🛡️ Audit Logs</h1>

      <div className="audit-table-wrapper">
        <table className="min-w-full border border-gray-600 text-sm">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-4 py-2 border">User</th>
              <th className="px-4 py-2 border">Action</th>
              <th className="px-4 py-2 border">Timestamp (Vilnius)</th>
            </tr>
          </thead>
          <tbody>
            {logs.length > 0 ? (
              logs.map(log => (
                <tr key={log.id} className="hover:bg-gray-700">
                  <td className="px-4 py-2 border">{log.user}</td>
                  <td className="px-4 py-2 border">{log.action}</td>
                  <td className="px-4 py-2 border">
                    {new Date(new Date(log.timestamp).getTime() + 3 * 60 * 60 * 1000).toLocaleString("en-GB", {
                      year: "numeric",
                      month: "2-digit",
                      day: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                      hour12: false
                    })}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="3" className="text-center py-4">No logs found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

}
