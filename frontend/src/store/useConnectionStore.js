import { create } from 'zustand';

export const useConnectionStore = create((set) => ({
  status: 'disconnected', // 'connecting' | 'connected' | 'disconnected' | 'error'
  setStatus: (status) => set({ status }),
}));
