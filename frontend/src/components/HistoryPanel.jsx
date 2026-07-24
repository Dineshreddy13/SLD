import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, ChevronUp, Trash2, Volume2, Loader2 } from 'lucide-react';
import { useSentenceStore } from '../store/useSentenceStore';
import { useUIStore } from '../store/useUIStore';
import { getRelativeTime } from '../utils/time';
import { playTTS } from '../api/tts';

const HistoryPanel = () => {
  const history = useSentenceStore((state) => state.history);
  const clearHistory = useSentenceStore((state) => state.clearHistory);
  const historyCollapsed = useUIStore((state) => state.historyCollapsed);
  const toggleHistoryCollapsed = useUIStore((state) => state.toggleHistoryCollapsed);

  const [confirmClear, setConfirmClear] = useState(false);
  const [playingId, setPlayingId] = useState(null);
  const confirmTimeoutRef = useRef(null);

  // Auto-revert clear confirmation after a few seconds
  useEffect(() => {
    if (confirmClear) {
      confirmTimeoutRef.current = setTimeout(() => {
        setConfirmClear(false);
      }, 3000);
    }
    return () => {
      if (confirmTimeoutRef.current) clearTimeout(confirmTimeoutRef.current);
    };
  }, [confirmClear]);

  const handleClearClick = () => {
    if (confirmClear) {
      clearHistory();
      setConfirmClear(false);
    } else {
      setConfirmClear(true);
    }
  };

  const handleSpeak = async (item, index) => {
    if (playingId !== null) return;
    
    setPlayingId(index);
    try {
      await playTTS(item.text);
    } catch (err) {
      console.error('Failed to play history item', err);
    } finally {
      setPlayingId(null);
    }
  };

  return (
    <div className="w-full bg-surface border border-border rounded-2xl overflow-hidden mt-6 mb-12 shadow-sm">
      
      {/* Header Row (Toggle) */}
      <button
        onClick={toggleHistoryCollapsed}
        aria-expanded={!historyCollapsed}
        aria-controls="history-content"
        className="w-full px-6 py-4 flex items-center justify-between bg-surface hover:bg-surface-raised transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-accent-signal"
      >
        <div className="flex items-center gap-3">
          <span className="font-sans font-semibold text-text-primary">History</span>
          <span className="bg-surface-raised text-text-secondary text-xs font-mono font-medium px-2 py-0.5 rounded-full border border-border">
            {history.length}
          </span>
        </div>
        <div className="text-text-secondary motion-safe:transition-transform motion-safe:duration-200">
          {historyCollapsed ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
        </div>
      </button>

      {/* Content Area */}
      {!historyCollapsed && (
        <div id="history-content" className="p-6 pt-2 border-t border-border">
          
          {history.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-text-secondary italic">
                Sentences you build will be saved here once you clear or complete one.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              
              <div className="flex justify-end mb-4">
                <button
                  onClick={handleClearClick}
                  aria-label={confirmClear ? "Confirm clear history" : "Clear history"}
                  className="flex items-center gap-2 px-3 py-1.5 bg-surface text-accent-warm hover:bg-accent-warm/10 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-accent-warm transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>{confirmClear ? "Confirm clear?" : "Clear history"}</span>
                </button>
              </div>

              <ul className="space-y-3">
                {history.map((item, idx) => {
                  // iterate in reverse so newest is on top
                  const reversedIdx = history.length - 1 - idx;
                  const currentItem = history[reversedIdx];
                  const isPlaying = playingId === reversedIdx;

                  return (
                    <li key={reversedIdx} className="flex items-center justify-between gap-4 p-4 bg-surface-raised border border-border rounded-xl">
                      <div className="flex flex-col gap-1 overflow-hidden">
                        <span className="font-mono text-lg text-text-primary truncate" title={currentItem.text}>
                          {currentItem.text}
                        </span>
                        <span className="text-xs text-text-secondary">
                          {getRelativeTime(currentItem.timestamp)}
                        </span>
                      </div>
                      
                      <button
                        onClick={() => handleSpeak(currentItem, reversedIdx)}
                        disabled={playingId !== null && !isPlaying}
                        aria-label={`Speak sentence: ${currentItem.text}`}
                        className="flex-shrink-0 p-2.5 rounded-lg bg-surface border border-border text-text-primary hover:bg-border focus:outline-none focus:ring-2 focus:ring-accent-signal transition-colors disabled:opacity-50"
                      >
                        {isPlaying ? (
                          <Loader2 className="w-4 h-4 animate-spin text-accent-signal" />
                        ) : (
                          <Volume2 className="w-4 h-4" />
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>

            </div>
          )}
          
        </div>
      )}
    </div>
  );
};

export default HistoryPanel;
