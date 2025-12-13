import React from "react";
import ReactDOM from "react-dom/client";
import Dashboard from "./Dashboard";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found");
}

ReactDOM.createRoot(rootElement).render(
  <Dashboard />
);
