// Questionnaire.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom"; // useNavigate is used for programmatic navigation
import "./App.css";

const ConfirmModal = ({ onConfirm, onCancel }) => (
  <div className="modal-overlay">
    <div className="modal-box">
      <h3>Are you sure?</h3>
      <p>Please confirm your answers before submitting.</p>
      <div className="modal-buttons">
        <button className="btn confirm" onClick={onConfirm}>Yes, Submit</button>
        <button className="btn cancel" onClick={onCancel}>Cancel</button>
      </div>
    </div>
  </div>
);

const Questionnaire = () => {
  const [step, setStep] = useState(1);
  const [showConfirm, setShowConfirm] = useState(false);;
  const [formData, setFormData] = useState({
    mustHaves: [],
    useCases: [],
    seats: "",
    vehicleType: "",
    snowDriving: "",
    fuelType: "",
    fuelEfficiencyImportance: "",
    interiorSpace: "",
    mainNeeds: []
  });

const navigate = useNavigate();

  const handleCheckbox = (field, value) => {
    setFormData((prev) => {
      const updated = prev[field].includes(value)
        ? prev[field].filter((v) => v !== value)
        : [...prev[field], value];
      return { ...prev, [field]: updated };
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    setShowConfirm(true);
  };
  
  const handleFinalSubmit = async () => {
    const token = localStorage.getItem("token");
    try {
      const res = await fetch("http://localhost:5000/submit_questionnaire", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });
  
      const data = await res.json();
      setShowConfirm(false);
      navigate("/recommendation", { state: { recommendation: data.recommendation } });
    } catch (err) {
      alert("Failed to submit.");
    }
  };

  const nextStep = () => setStep((s) => s + 1);
  const prevStep = () => setStep((s) => s - 1);

  const steps = [
    <>
      <h2>What are your must-haves?</h2>
      {[
        "Fuel economy",
        "Performance and handling",
        "Interior style",
        "Affordability",
        "Interior cargo space",
        "Features and accessories",
        "Passenger space",
        "Driving in snow"
      ].map((item) => (
        <label key={item}><input type="checkbox" checked={formData.mustHaves.includes(item)} onChange={() => handleCheckbox("mustHaves", item)} /> {item}</label>
      ))}
    </>,
    <>
      <h2>What will you use this car for?</h2>
      {[
        "Household errands",
        "Daily commute",
        "Outdoor activities",
        "Offroad driving",
        "Longer road trips",
        "Driving kids and their stuff",
        "Fun car/guilty pleasure"
      ].map((item) => (
        <label key={item}><input type="checkbox" checked={formData.useCases.includes(item)} onChange={() => handleCheckbox("useCases", item)} /> {item}</label>
      ))}
    </>,
    <>
      <h2>How many total seats do you need?</h2>
      {[
        "2 Seats",
        "3-5 Seats",
        "6-8 Seats",
        "8+ Seats"
      ].map((item) => (
        <label key={item}><input type="radio" name="seats" value={item} checked={formData.seats === item} onChange={handleChange} /> {item}</label>
      ))}
    </>,
    <>
      <h2>What is your preferred type of vehicle?</h2>
      {[
        "Convertibles",
        "Coupes",
        "Hatchbacks",
        "Wagons",
        "Sedans",
        "SUVs",
        "Minivans",
        "Vans",
        "Trucks"
      ].map((item) => (
        <label key={item}><input type="radio" name="vehicleType" value={item} checked={formData.vehicleType === item} onChange={handleChange} /> {item}</label>
      ))}
    </>,
    <>
      <h2>Do you often drive in snow or difficult conditions?</h2>
      {[
        { label: "Yes", value: "yes" },
        { label: "No", value: "no" }
      ].map((opt) => (
        <label key={opt.value}><input type="radio" name="snowDriving" value={opt.value} checked={formData.snowDriving === opt.value} onChange={handleChange} /> {opt.label}</label>
      ))}
    </>,
    <>
      <h2>Do you have a fuel type preference?</h2>
      {[
        "Gasoline",
        "Diesel",
        "Hybrid",
        "Electric"
      ].map((type) => (
        <label key={type}><input type="radio" name="fuelType" value={type} checked={formData.fuelType === type} onChange={handleChange} /> {type}</label>
      ))}
    </>,
    <>
      <h2>How important is fuel efficiency to you?</h2>
      {[
        "Very important",
        "Important",
        "Not important"
      ].map((level) => (
        <label key={level}><input type="radio" name="fuelEfficiencyImportance" value={level} checked={formData.fuelEfficiencyImportance === level} onChange={handleChange} /> {level}</label>
      ))}
    </>,
    <>
      <h2>Is interior space important to you?</h2>
      {[
        { label: "Yes", value: "yes" },
        { label: "No", value: "no" }
      ].map((opt) => (
        <label key={opt.value}><input type="radio" name="interiorSpace" value={opt.value} checked={formData.interiorSpace === opt.value} onChange={handleChange} /> {opt.label}</label>
      ))}
    </>,
    <>
      <h2>What are your main needs for using the car?</h2>
      {[
        "Daily use",
        "Long trips",
        "Carrying kids and their things",
        "Business purposes"
      ].map((item) => (
        <label key={item}><input type="checkbox" checked={formData.mainNeeds.includes(item)} onChange={() => handleCheckbox("mainNeeds", item)} /> {item}</label>
      ))}
    </>,
    <>
    <h2>Review your answers</h2>
    <div style={{ textAlign: "left", color: "#eee", lineHeight: "1.6" }}>
      <strong>Must-Haves:</strong>
      <ul>{formData.mustHaves.map((item, i) => <li key={i}>{item}</li>)}</ul>
  
      <strong>Use Cases:</strong>
      <ul>{formData.useCases.map((item, i) => <li key={i}>{item}</li>)}</ul>
  
      <p><strong>Seating:</strong> {formData.seats}</p>
      <p><strong>Vehicle Type:</strong> {formData.vehicleType}</p>
      <p><strong>Drives in Snow:</strong> {formData.snowDriving}</p>
      <p><strong>Fuel Type:</strong> {formData.fuelType}</p>
      <p><strong>Fuel Efficiency Importance:</strong> {formData.fuelEfficiencyImportance}</p>
      <p><strong>Interior Space Important:</strong> {formData.interiorSpace}</p>
  
      <strong>Main Needs:</strong>
      <ul>{formData.mainNeeds.map((item, i) => <li key={i}>{item}</li>)}</ul>
    </div>
    <button className="btn" onClick={handleSubmit}>Submit</button>
  </>
  ];

  return (
    <div className="form-container">
      {steps[step - 1]}
      <div style={{ marginTop: "1rem" }}>
        {step > 1 && <button className="btn" onClick={prevStep}>Back</button>}
        {step < steps.length && <button className="btn" onClick={nextStep}>Next</button>}
      </div>
      {showConfirm && (
        <ConfirmModal onConfirm={handleFinalSubmit} onCancel={() => setShowConfirm(false)} />
      )}  
    </div>
  );
};

export default Questionnaire;