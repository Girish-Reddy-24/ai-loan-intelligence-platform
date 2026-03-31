import React, { useState } from "react";
import axios from "axios";

function App() {
  const [form, setForm] = useState({
    annual_income: "",
    monthly_income: "",
    monthly_expenses: "",
    loan_amount: "",
    existing_debt_payments_monthly: 0,
    credit_score: ""
  });

  const [result, setResult] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [simulation, setSimulation] = useState(null);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: Number(e.target.value)
    });
  };

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/predict", form);
      setResult(res.data);
      setExplanation(null);
      setSimulation(null);
    } catch {
      alert("Backend error");
    }
  };

  const getExplanation = async () => {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/explanation/${result.request_id}`
      );

      setExplanation(res.data.explanation);
    } catch {
      alert("Explanation error");
    }
  };

  const runSimulation = async () => {
    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/simulate",
        {
          ...form,

          // 🔥 CRITICAL FIX (ensures backend gets this)
          existing_debt_payments_monthly:
            form.existing_debt_payments_monthly || 0
        }
      );

      console.log("Simulation response:", res.data);

      setSimulation(res.data.simulation);
    } catch {
      alert("Simulation error");
    }
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h2>🏦 AI Loan Decision System</h2>

      <input name="annual_income" placeholder="Annual Income" onChange={handleChange} /><br />
      <input name="monthly_income" placeholder="Monthly Income" onChange={handleChange} /><br />
      <input name="monthly_expenses" placeholder="Monthly Expenses" onChange={handleChange} /><br />
      <input name="loan_amount" placeholder="Loan Amount" onChange={handleChange} /><br />
      <input name="credit_score" placeholder="Credit Score" onChange={handleChange} /><br />

      <button onClick={handleSubmit}>Check Loan Decision</button>

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>Result</h3>

          <p><b>Prediction:</b> {result.prediction}</p>
          <p><b>Risk:</b> {result.risk_level}</p>
          <p><b>Offer:</b> {result.offer}</p>
          <p><b>Confidence:</b> {result.confidence_score}</p>

          <h4>Why this decision?</h4>
          <ul>
            {result.reasons?.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>

          <h4>Simulation</h4>
          <button onClick={runSimulation}>Run Simulation</button>

          {simulation && (
            <div>
              {/* 🔥 FIXED FIELD NAME */}
              <p><b>Max Safe Loan:</b> ${simulation.max_safe_loan || 0}</p>

              {/* 🔥 FIXED PERCENT DISPLAY */}
              <p>
                <b>Approval Probability:</b>{" "}
                {Math.round((simulation.approval_probability || 0) * 100)}%
              </p>

              {/* OPTIONAL: show recommendations */}
              {simulation.recommendations && (
                <div>
                  <h5>Recommendations:</h5>
                  <ul>
                    {simulation.recommendations.map((rec, i) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          <h4>AI Explanation</h4>
          <button onClick={getExplanation}>Get Explanation</button>

          {explanation && (
            <div style={{ background: "#f5f5f5", padding: "10px" }}>
              <pre>{explanation}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;