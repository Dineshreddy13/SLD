import { useEffect, useRef, useCallback } from 'react';
import { useConnectionStore } from '../store/useConnectionStore';
import { usePredictionStore } from '../store/usePredictionStore';
import { useSentenceStore } from '../store/useSentenceStore';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/predict';

export function useWebSocket() {
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const backoffRef = useRef(1000);
  
  const setStatus = useConnectionStore((state) => state.setStatus);
  const setPrediction = usePredictionStore((state) => state.setPrediction);
  const addLetter = useSentenceStore((state) => state.addLetter);

  const connect = useCallback(() => {
    // Prevent multiple connections
    if (wsRef.current?.readyState === WebSocket.CONNECTING || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setStatus('connected');
      backoffRef.current = 1000; // Reset backoff on successful connection
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Update predictions and top3, etc.
        setPrediction(data);
        
        // Check for new confirmed letters (local optimistic update, mostly for hooks/triggers if needed)
        if (data.stable_prediction && data.stable_prediction.is_new) {
          addLetter(data.stable_prediction.label);
        }
        
        // Always strictly sync the sentence from the server (source of truth)
        if (data.sentence !== undefined) {
          useSentenceStore.setState({ sentence: data.sentence });
        }
        
      } catch (err) {
        console.error("Failed to parse websocket message", err);
      }
    };

    ws.onclose = () => {
      setStatus('disconnected');
      
      // Auto-reconnect with exponential backoff (capped at ~10s)
      reconnectTimeoutRef.current = setTimeout(() => {
        backoffRef.current = Math.min(backoffRef.current * 2, 10000);
        connect();
      }, backoffRef.current);
    };

    ws.onerror = () => {
      setStatus('error');
      // The onclose event will handle the reconnection attempt
    };

    wsRef.current = ws;
  }, [setStatus, setPrediction, addLetter]);

  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        // Remove listeners so we don't trigger reconnections on unmount
        wsRef.current.onclose = null;
        wsRef.current.onerror = null;
        wsRef.current.close();
        wsRef.current = null;
      }
      setStatus('disconnected');
    };
  }, [connect, setStatus]);

  const sendFrame = useCallback((blob) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(blob);
    }
  }, []);

  const sendControlAction = useCallback((action) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action }));
    }
  }, []);

  return { sendFrame, sendControlAction };
}
