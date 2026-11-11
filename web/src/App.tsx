import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { TermRoute } from "./routes/TermRoute";
import { WelcomeRoute } from "./routes/WelcomeRoute";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<WelcomeRoute />} />
          <Route path="term/:slug" element={<TermRoute />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
