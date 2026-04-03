import React, { useState } from "react";
import axios from "axios";

function App() {
  const [form, setForm] = useState({
    annual_income: "",
    monthly_expenses: "",
    loan_amount: "",
    existing_debt_payments_monthly: 0,
    credit_score: ""
  });

  const [result, setResult] = useState(null);
  const [simulation, setSimulation] = useState(null);

  // =========================
  // HANDLE INPUT
  // =========================
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: Number(e.target.value)
    });
  };

  // =========================
  // VALIDATION + PREDICT
  // =========================
  const handleSubmit = async () => {
    // ✅ VALIDATION
    if (!form.annual_income || form.annual_income <= 0) {
      alert("Enter valid annual income");
      return;
    }

    if (!form.loan_amount || form.loan_amount <= 0) {
      alert("Enter valid loan amount");
      return;
    }

    if (!form.credit_score || form.credit_score < 300 || form.credit_score > 900) {
      alert("Enter valid credit score (300–900)");
      return;
    }

    try {
      const res = await axios.post(
        "https://ai-loan-intelligence-platform.onrender.com/predict",
        form
      );

      setResult(res.data);
      setSimulation(null);
    } catch {
      alert("Backend error");
    }
  };

  // =========================
  // SIMULATION
  // =========================
  const runSimulation = async () => {
    try {
      const res = await axios.post(
        "https://ai-loan-intelligence-platform.onrender.com/simulate",
        {
          ...form,
          existing_debt_payments_monthly:
            form.existing_debt_payments_monthly || 0
        }
      );

      setSimulation(res.data.simulation);
    } catch {
      alert("Simulation error");
    }
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h2>🏦 AI Loan Decision System</h2>

      {/* ========================= INPUTS ========================= */}
      <input
        name="annual_income"
        placeholder="Annual Income"
        onChange={handleChange}
      /><br />

      {/* ✅ AUTO CALCULATED MONTHLY */}
      {form.annual_income > 0 && (
        <p>
          Monthly Income: <b>${Math.round(form.annual_income / 12)}</b>
        </p>
      )}

      <input
        name="monthly_expenses"
        placeholder="Monthly Expenses"
        onChange={handleChange}
      /><br />

      <input
        name="loan_amount"
        placeholder="Loan Amount"
        onChange={handleChange}
      /><br />

      <input
        name="existing_debt_payments_monthly"
        placeholder="Existing Debt (Optional)"
        onChange={handleChange}
      /><br />

      <input
        name="credit_score"
        placeholder="Credit Score"
        onChange={handleChange}
      /><br />

      <button onClick={handleSubmit}>Check Loan Decision</button>

      {/* ========================= RESULT ========================= */}
      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>Result</h3>

          <p><b>Prediction:</b> {result.prediction}</p>
          <p><b>Risk:</b> {result.risk_level}</p>
          <p><b>Confidence:</b> {result.confidence_score}</p>

          <h4>Why this decision?</h4>
          <ul>
            {result.reasons?.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>

          {/* ========================= SIMULATION ========================= */}
          <h4>Simulation</h4>
          <button onClick={runSimulation}>Run Simulation</button>

          {simulation && (
            <div>
              <p>
                <b>Max Safe Loan:</b> ${simulation.max_safe_loan || 0}
              </p>

              <p>
                <b>Approval Probability:</b>{" "}
                {Math.round((simulation.approval_probability || 0) * 100)}%
              </p>

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

          {/* ========================= AI EXPLANATION ========================= */}
          <h4>AI Explanation</h4>
          <div style={{ background: "#f5f5f5", padding: "10px" }}>
            <pre>{result.explanation}</pre>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;