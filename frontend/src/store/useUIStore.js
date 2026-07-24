import { create } from 'zustand';

const getInitialDarkMode = () => {
  try {
    const saved = localStorage.getItem('sld-dark-mode');
    if (saved !== null) {
      return JSON.parse(saved);
    }
  } catch (e) {
    console.error('Failed to parse dark mode from localStorage', e);
  }
  return false; // default to false
};

export const useUIStore = create((set) => ({
  darkMode: getInitialDarkMode(),
  historyCollapsed: true,
  
  toggleDarkMode: () => set((state) => {
    const nextMode = !state.darkMode;
    try {
      localStorage.setItem('sld-dark-mode', JSON.stringify(nextMode));
    } catch (e) {
      console.error('Failed to save dark mode to localStorage', e);
    }
    return { darkMode: nextMode };
  }),
  
  toggleHistoryCollapsed: () => set((state) => ({ historyCollapsed: !state.historyCollapsed }))
}));
