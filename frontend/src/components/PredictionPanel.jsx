import React from 'react';
import { usePredictionStore } from '../store/usePredictionStore';

// Subtle SVG pattern to resemble hand landmarks in an idle state
const IdleHandNodePattern = () => (
  <div className="flex flex-col items-center justify-center space-y-4 py-8">
    <svg 
      width="120" 
      height="140" 
      viewBox="0 0 120 140" 
      className="text-text-secondary motion-safe:animate-pulse opacity-20"
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2"
    >
      {/* Abstract hand/node lines */}
      <path d="M60 120 L60 80" />
      <path d="M60 80 L30 40 L35 20" />
      <path d="M60 80 L50 30 L55 10" />
      <path d="M60 80 L75 30 L80 15" />
      <path d="M60 80 L95 45 L105 30" />
      
      {/* Nodes (joints) */}
      <circle cx="60" cy="120" r="4" fill="currentColor" />
      <circle cx="60" cy="80" r="4" fill="currentColor" />
      <circle cx="30" cy="40" r="3" fill="currentColor" />
      <circle cx="35" cy="20" r="3" fill="currentColor" />
      <circle cx="50" cy="30" r="3" fill="currentColor" />
      <circle cx="55" cy="10" r="3" fill="currentColor" />
      <circle cx="75" cy="30" r="3" fill="currentColor" />
      <circle cx="80" cy="15" r="3" fill="currentColor" />
      <circle cx="95" cy="45" r="3" fill="currentColor" />
      <circle cx="105" cy="30" r="3" fill="currentColor" />
    </svg>
    <p className="text-text-secondary text-sm font-medium tracking-wide text-center">
      Show a hand sign to begin
    </p>
  </div>
);

const PredictionPanel = () => {
  const { stablePrediction, rawPrediction, handDetected, top3 } = usePredictionStore();

  if (!handDetected) {
    return (
      <div className="h-full bg-surface-raised border border-border rounded-2xl flex items-center justify-center p-6">
        <IdleHandNodePattern />
      </div>
    );
  }

  // Use the raw prediction to drive the live visual feedback, but the stable prediction
  // represents the actual confirmed letter.
  const activeLabel = stablePrediction?.label || rawPrediction?.label || '?';
  const confidence = rawPrediction ? rawPrediction.confidence * 100 : 0;
  
  // High confidence uses accent-signal, low uses a neutral border tone.
  const isHighConfidence = confidence > 70;
  const barColor = isHighConfidence ? 'bg-accent-signal' : 'bg-text-secondary';
  const displayConf = confidence.toFixed(1);

  return (
    <div className="h-full bg-surface-raised border border-border rounded-2xl p-6 flex flex-col justify-between">
      
      <div className="flex flex-col items-center justify-center flex-grow py-6">
        <div className="text-[8rem] leading-none font-mono font-bold text-text-primary tracking-tighter">
          {activeLabel}
        </div>
      </div>

      <div className="space-y-6">
        {/* Confidence Meter */}
        <div className="space-y-2">
          <div className="flex justify-between items-end">
            <span className="text-xs uppercase font-bold text-text-secondary tracking-widest">Confidence</span>
            <span className="font-mono text-sm text-text-primary">{displayConf}%</span>
          </div>
          <div className="h-2 w-full bg-surface rounded-full overflow-hidden">
            <div 
              className={`h-full ${barColor} motion-safe:transition-all motion-safe:duration-150 ease-out`}
              style={{ width: `${confidence}%` }}
            />
          </div>
        </div>

        {/* Top 3 Predictions */}
        {top3 && top3.length > 0 && (
          <div className="space-y-2 pt-4 border-t border-border">
            <span className="text-xs uppercase font-bold text-text-secondary tracking-widest block mb-3">Top Matches</span>
            {top3.map((pred, idx) => (
              <div key={idx} className="flex justify-between items-center text-sm">
                <span className="text-text-secondary font-medium">{pred.label}</span>
                <span className="text-text-secondary font-mono">{(pred.confidence * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};

export default PredictionPanel;
