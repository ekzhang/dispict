import "./app.css";
import "@fontsource/roboto-flex/variable-full.css";
import "@fontsource/source-serif-4/400.css";
import "@fontsource/source-serif-4/400-italic.css";

import App from "./App.svelte";

const app = new App({
  target: document.getElementById("app"),
});

export default app;
