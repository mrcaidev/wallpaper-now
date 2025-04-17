import "@fontsource-variable/inter/index.css";
import "@fontsource/rochester/index.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./app.tsx";
import "./global.css";

createRoot(document.getElementById("root") as HTMLDivElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
