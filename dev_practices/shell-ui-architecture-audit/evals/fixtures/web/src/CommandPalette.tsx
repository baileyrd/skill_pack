import { useEffect, useState } from "react";

const COMMANDS = ["Go to Billing", "Go to Users", "Toggle sidebar", "Sign out"];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    window.addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.key === "k") setOpen(true);
    });
  }, []);

  if (!open) return null;
  return (
    <div className="palette-backdrop">
      <div className="palette">
        <input value={query} onChange={(e) => setQuery(e.target.value)} />
        {COMMANDS.filter((c) => c.toLowerCase().includes(query.toLowerCase())).map((c) => (
          <div key={c} className="palette-item">{c}</div>
        ))}
      </div>
    </div>
  );
}
