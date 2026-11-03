import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { CommandPalette } from "./CommandPalette";
import { useShell } from "./store";
import "./theme.css";

const Billing = () => <div>billing</div>;
const Users = () => <div>users</div>;

export function App() {
  const { sidebarOpen, toggleSidebar } = useShell();
  return (
    <BrowserRouter>
      <div className="shell">
        <div className="topbar" onClick={toggleSidebar}>☰ Acme Console</div>
        {sidebarOpen && (
          <div className="sidebar">
            <Link to="/billing">Billing</Link>
            <Link to="/users">Users</Link>
          </div>
        )}
        <div className="content">
          <Routes>
            <Route path="/billing" element={<Billing />} />
            <Route path="/users" element={<Users />} />
          </Routes>
        </div>
        <CommandPalette />
      </div>
    </BrowserRouter>
  );
}
