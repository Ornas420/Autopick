// Recommendation.jsx
import { useLocation, useNavigate } from "react-router-dom";
import "./App.css";

const Recommendation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const recommendation = location.state?.recommendation;

  const [listPart, summaryPart] = recommendation
    ? recommendation.split(/\n\n|\n_\*/)
    : ["", ""];

  const carList = listPart.split(/\n+/).filter(line => line.trim() !== "");

  return (
    <div className="home-container">
      <div className="form-container">
        <h2>Recommended Cars</h2>
        {recommendation ? (
          <>
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
          </>
        ) : (
          <>
            <p>No suitable cars found for the selected preferences.</p>
            <button className="btn" onClick={() => navigate("/questionnaire")}>Back to Questionnaire</button>
          </>
        )}
      </div>
    </div>
  );
};

export default Recommendation;
