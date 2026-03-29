import React, { useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

function App() {
  const [income, setIncome] = useState(80000);
  const [expenses, setExpenses] = useState(3000);
  const [loan, setLoan] = useState(200000);
  const [credit, setCredit] = useState(700);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [requestId, setRequestId] = useState("");
  const [explanation, setExplanation] = useState("");
  const [expLoading, setExpLoading] = useState(false);
  const [simulation, setSimulation] = useState(null);

  // =========================
  // SUBMIT
  // =========================
  const handleSubmit = async () => {
    setLoading(true);
    setResult(null);
    setExplanation("");
    setSimulation(null);

    try {
      const res = await axios.post("http://localhost:8000/predict", {
        annual_income: Number(income),
        monthly_income: Number(income) / 12,
        monthly_expenses: Number(expenses),
        loan_amount: Number(loan),
        existing_debt_payments_monthly: 500,
        credit_score: Number(credit),
        num_credit_accounts: 5,
        property_value: 300000,
      });

      setResult(res.data);
      setRequestId(res.data.request_id);
    } catch {
      alert("❌ Error connecting to backend");
    }

    setLoading(false);
  };

  // =========================
  // EXPLANATION
  // =========================
  const getExplanation = async () => {
    setExpLoading(true);

    try {
      const res = await axios.get(
        `http://localhost:8000/explanation/${requestId}`
      );

      if (res.data.explanation) {
        setExplanation(res.data.explanation);
      } else {
        setExplanation("⏳ Still generating... try again");
      }
    } catch {
      setExplanation("❌ Error fetching explanation");
    }

    setExpLoading(false);
  };

  // =========================
  // SIMULATION
  // =========================
  const runSimulation = async () => {
    try {
      const res = await axios.post("http://localhost:8000/simulate", {
        annual_income: Number(income),
        monthly_income: Number(income) / 12,
        monthly_expenses: Number(expenses),
        loan_amount: Number(loan),
        existing_debt_payments_monthly: 500,
        credit_score: Number(credit),
      });

      setSimulation(res.data.simulation);
    } catch {
      alert("❌ Simulation failed");
    }
  };

  return (
    <div style={containerStyle}>
      <div style={{ width: "100%", maxWidth: "900px" }}>
        <h1 style={{ textAlign: "center" }}>🏦 AI Loan Decision System</h1>

        {/* ================= FORM ================= */}
        <div style={cardStyle}>
          <h3>Enter Details</h3>

          <div style={gridStyle}>
            <SliderInput label="Annual Income ($)" value={income} setValue={setIncome} min={10000} max={200000} />
            <SliderInput label="Monthly Expenses ($)" value={expenses} setValue={setExpenses} min={500} max={10000} />
            <SliderInput label="Loan Amount ($)" value={loan} setValue={setLoan} min={1000} max={300000} />
            <SliderInput label="Credit Score" value={credit} setValue={setCredit} min={300} max={850} />
          </div>

          <button onClick={handleSubmit} style={buttonStyle}>
            Check Loan Decision
          </button>
        </div>

        {/* ================= LOADING ================= */}
        {loading && <h3 style={{ textAlign: "center" }}>Analyzing...</h3>}

        {/* ================= RESULT ================= */}
        {result && !loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={cardStyle}>
            <h2>Result</h2>

            <p>
              <b>Prediction:</b>{" "}
              <span style={{
                color: result.prediction === "Approved" ? "green" : "red",
                fontWeight: "bold"
              }}>
                {result.prediction}
              </span>
            </p>

            <p><b>Risk:</b> {result.risk_level}</p>
            <p><b>Offer:</b> {result.offer}</p>

            {/* ================= CHART ================= */}
            <h3>Confidence</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={[
                { name: "Confidence", value: result.confidence_score * 100 }
              ]}>
                <XAxis dataKey="name" />
                <Tooltip />
                <Bar dataKey="value" />
              </BarChart>
            </ResponsiveContainer>

            {/* ================= REASONS ================= */}
            <h3>Why this decision?</h3>
            <ul>
              {result.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>

            {/* ================= SHAP ================= */}
            <h3>Top Factors (AI Insights)</h3>
            <ul>
              {result.shap_explanation.map((item, i) => (
                <li key={i}>
                  {item.feature} → {item.impact > 0 ? "Positive" : "Negative"}
                </li>
              ))}
            </ul>

            {/* ================= SIMULATION ================= */}
            <button onClick={runSimulation} style={buttonStyle}>
              Run What-If Simulation
            </button>

            {simulation && (
              <div style={cardStyle}>
                <h3>Smart Recommendation</h3>
                <p><b>Max Safe Loan:</b> ${simulation.max_safe_loan}</p>
                <p><b>Approval Probability:</b> {simulation.approval_probability * 100}%</p>

                <ul>
                  {simulation.recommendations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* ================= EXPLANATION ================= */}
            <h3>AI Explanation</h3>

            <button onClick={getExplanation} style={buttonStyle}>
              {expLoading ? "Loading..." : "Get Explanation"}
            </button>

            <div style={explanationStyle}>
              {explanation || "Click button to generate explanation"}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

// ================= SLIDER COMPONENT =================
function SliderInput({ label, value, setValue, min, max }) {
  return (
    <div>
      <label style={{ fontWeight: "bold" }}>
        {label}: {value}
      </label>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        style={{ width: "100%" }}
      />
    </div>
  );
}

// ================= STYLES =================
const containerStyle = {
  fontFamily: "Inter",
  minHeight: "100vh",
  background: "#eef2f3",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  padding: "20px"
};

const cardStyle = {
  background: "white",
  padding: "20px",
  borderRadius: "12px",
  boxShadow: "0 5px 15px rgba(0,0,0,0.1)",
  marginTop: "20px"
};

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: "15px"
};

const buttonStyle = {
  marginTop: "20px",
  width: "100%",
  padding: "12px",
  background: "#4facfe",
  color: "white",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer"
};

const explanationStyle = {
  background: "#f4f6f8",
  padding: "15px",
  borderRadius: "8px",
  marginTop: "10px"
};

export default App;