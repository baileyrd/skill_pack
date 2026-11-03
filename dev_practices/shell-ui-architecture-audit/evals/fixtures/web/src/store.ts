import { create } from "zustand";

type Shell = { sidebarOpen: boolean; theme: string; toggleSidebar: () => void };

const saved = JSON.parse(localStorage.getItem("shell") || "{}");

export const useShell = create<Shell>((set, get) => ({
  sidebarOpen: saved.sidebarOpen ?? true,
  theme: saved.theme ?? "light",
  toggleSidebar: () => {
    set({ sidebarOpen: !get().sidebarOpen });
    localStorage.setItem("shell", JSON.stringify(get()));
  },
}));
