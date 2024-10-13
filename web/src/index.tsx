import { createRoot } from "react-dom/client";
import { Main } from "./main";
import "./index.css";
import "@mantine/core/styles.css";
const container = document.querySelector("#root");
if (container) {
  const root = createRoot(container);
  root.render(<Main />);
} else {
  console.error("Root container not found");
}
