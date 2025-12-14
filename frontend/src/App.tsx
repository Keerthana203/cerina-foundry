import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import SubmitPage from "./SubmitPage";
import HistoryPage from "./HistoryPage";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={navStyle}>
        <strong>Cerina Protocol Foundry</strong>
        <div>
          <NavLink to="/" style={linkStyle}>Submit</NavLink>
          <NavLink to="/history" style={linkStyle}>Dashboard</NavLink>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<SubmitPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </BrowserRouter>
  );
}

const navStyle = {
  display: "flex",
  justifyContent: "space-between",
  padding: "12px 20px",
  borderBottom: "1px solid #ddd",
};

const linkStyle = {
  marginLeft: 12,
  textDecoration: "none",
  fontWeight: 500,
};
