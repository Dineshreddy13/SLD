import { create } from 'zustand';

export const useSentenceStore = create((set) => ({
  sentence: '',
  history: [], // array of { text: string, timestamp: number }
  
  addLetter: (letter) => set((state) => ({
    sentence: state.sentence + letter
  })),
  
  addSpace: () => set((state) => {
    // Prevent starting with a space or double spaces
    if (state.sentence.length > 0 && !state.sentence.endsWith(' ')) {
      return { sentence: state.sentence + ' ' };
    }
    return state;
  }),
  
  deleteLast: () => set((state) => {
    if (state.sentence.length > 0) {
      return { sentence: state.sentence.slice(0, -1) };
    }
    return state;
  }),
  
  clear: () => set((state) => {
    if (state.sentence.trim().length > 0) {
      return {
        sentence: '',
        history: [...state.history, { text: state.sentence.trim(), timestamp: Date.now() }]
      };
    }
    return { sentence: '' };
  }),
  
  clearHistory: () => set({ history: [] })
}));
