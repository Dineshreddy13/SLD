import { create } from 'zustand';

export const usePredictionStore = create((set) => ({
  rawPrediction: null,
  stablePrediction: null,
  handDetected: false,
  top3: [],
  setPrediction: (data) => set((state) => ({
    rawPrediction: data.raw_prediction !== undefined ? data.raw_prediction : state.rawPrediction,
    stablePrediction: data.stable_prediction !== undefined ? data.stable_prediction : state.stablePrediction,
    handDetected: data.hand_detected !== undefined ? data.hand_detected : state.handDetected,
    top3: data.top_3 !== undefined ? data.top_3 : state.top3,
  })),
}));
