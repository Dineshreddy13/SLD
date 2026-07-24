import React, { useState } from 'react';
import { useSentenceStore } from '../store/useSentenceStore';
import { Space, Delete, Trash2, Volume2, Loader2 } from 'lucide-react';
import { playTTS } from '../api/tts';

const SentenceBuilder = ({ sendControlAction }) => {
  const sentence = useSentenceStore((state) => state.sentence);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleSpeak = async () => {
    if (!sentence || isPlaying) return;
    
    setIsPlaying(true);
    try {
      await playTTS(sentence);
    } catch (err) {
      console.error("TTS Playback failed", err);
    } finally {
      setIsPlaying(false);
    }
  };

  const isEmpty = sentence.length === 0;

  return (
    <div className="w-full bg-surface-raised border border-border rounded-2xl p-6 flex flex-col gap-6 shadow-sm">
      
      {/* Output Display */}
      <div className="bg-surface border border-border rounded-xl p-6 min-h-[120px] flex items-center relative overflow-hidden">
        {isEmpty ? (
          <span className="text-text-secondary font-mono italic text-lg opacity-70">
            Your translated sentence will appear here.
          </span>
        ) : (
          <div className="font-mono text-3xl tracking-wide text-text-primary break-all">
            {sentence}
            {/* Blinking cursor */}
            <span className="inline-block w-3 h-8 bg-accent-signal ml-1 align-middle motion-safe:animate-pulse" />
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        
        {/* Editing Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => sendControlAction('space')}
            aria-label="Add space"
            className="flex items-center gap-2 px-5 py-3 bg-surface border border-border text-text-primary rounded-lg font-medium hover:bg-border focus:outline-none focus:ring-2 focus:ring-accent-signal transition-colors"
          >
            <Space className="w-5 h-5" />
            <span>Space</span>
          </button>
          
          <button
            onClick={() => sendControlAction('delete')}
            aria-label="Delete last character"
            className="flex items-center gap-2 px-5 py-3 bg-surface border border-border text-text-primary rounded-lg font-medium hover:bg-border focus:outline-none focus:ring-2 focus:ring-accent-signal transition-colors"
          >
            <Delete className="w-5 h-5" />
            <span>Delete</span>
          </button>
          
          <button
            onClick={() => sendControlAction('clear')}
            aria-label="Clear sentence"
            className="flex items-center gap-2 px-5 py-3 bg-surface border border-accent-warm text-accent-warm rounded-lg font-medium hover:bg-accent-warm/10 focus:outline-none focus:ring-2 focus:ring-accent-warm transition-colors"
          >
            <Trash2 className="w-5 h-5" />
            <span>Clear</span>
          </button>
        </div>

        {/* TTS Control */}
        <button
          onClick={handleSpeak}
          disabled={isEmpty || isPlaying}
          aria-label="Speak sentence"
          className="flex items-center gap-2 px-6 py-3 bg-text-primary text-bg rounded-lg font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-surface-raised focus:ring-text-primary transition-all"
        >
          {isPlaying ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Speaking...</span>
            </>
          ) : (
            <>
              <Volume2 className="w-5 h-5" />
              <span>Speak</span>
            </>
          )}
        </button>

      </div>
    </div>
  );
};

export default SentenceBuilder;
