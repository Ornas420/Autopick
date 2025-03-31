// Recommendation.jsx
import { useLocation, useNavigate } from "react-router-dom";
import "./App.css";

const Recommendation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const recommendation = location.state?.recommendation;

  if (!recommendation) {
    return (
      <div className="form-container">
        <h2>No Recommendation Found</h2>
        <p>Try submitting the questionnaire again.</p>
        <button className="btn" onClick={() => navigate("/questionnaire")}>Back to Questionnaire</button>
      </div>
    );
  }

  // Split the recommendation: list vs summary
  const [listPart, summaryPart] = recommendation.split(/\n\n|\n_\*/);
  const carList = listPart.split(/\n+/).filter(line => line.trim() !== "");

  return (
    <div className="form-container">
      <h2>Recommended Cars</h2>
      <ul style={{ textAlign: "left", fontSize: "1rem" }}>
        {carList.map((car, index) => (
          <li key={index}>{car}</li>
        ))}
      </ul>
      {summaryPart && (
        <p style={{ fontStyle: "italic", fontSize: "0.9rem", marginTop: "1rem", opacity: 0.85 }}>
          {summaryPart.replace(/[_*]/g, "")}
        </p>
      )}
      <button className="btn" onClick={() => navigate("/")}>Go to Home</button>
    </div>
  );
};

export default Recommendation;