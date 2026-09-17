import { create } from "zustand";

type WSStore = {
  workspaceId: string;
  setWorkspace: (id: string) => void;
};

export const useWorkspace = create<WSStore>((set) => ({
  workspaceId: localStorage.getItem("cascudo:workspace") || "ws-demo",
  setWorkspace: (id: string) => {
    localStorage.setItem("cascudo:workspace", id);
    set({ workspaceId: id });
  },
}));
