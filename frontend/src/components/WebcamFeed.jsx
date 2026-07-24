import React, { useRef, useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { usePredictionStore } from '../store/usePredictionStore';

const WebcamFeed = forwardRef((props, ref) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null); // Offscreen canvas for capturing frames
  
  const [status, setStatus] = useState('loading'); // 'loading', 'active', 'denied', 'not_found', 'error'
  const streamRef = useRef(null);
  
  const handDetected = usePredictionStore((state) => state.handDetected);

  useEffect(() => {
    let active = true;

    const startCamera = async () => {
      try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          if (active) setStatus('not_found');
          return;
        }

        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } } 
        });
        
        if (!active) {
          // If unmounted while waiting for permission, stop tracks immediately
          stream.getTracks().forEach(track => track.stop());
          return;
        }

        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setStatus('active');
        
      } catch (err) {
        if (!active) return;
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
          setStatus('denied');
        } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
          setStatus('not_found');
        } else {
          console.error('Webcam error:', err);
          setStatus('error');
        }
      }
    };

    startCamera();

    return () => {
      active = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    };
  }, []);

  useImperativeHandle(ref, () => ({
    captureFrame: () => {
      return new Promise((resolve) => {
        if (status !== 'active' || !videoRef.current || !canvasRef.current) {
          resolve(null);
          return;
        }

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        
        // Calculate dimensions to max 480px wide while maintaining aspect ratio
        const maxWidth = 480;
        let drawWidth = video.videoWidth;
        let drawHeight = video.videoHeight;
        
        if (drawWidth > maxWidth) {
          const ratio = maxWidth / drawWidth;
          drawWidth = maxWidth;
          drawHeight = Math.floor(drawHeight * ratio);
        }
        
        // Ensure valid dimensions
        if (drawWidth === 0 || drawHeight === 0) {
          resolve(null);
          return;
        }

        canvas.width = drawWidth;
        canvas.height = drawHeight;
        
        ctx.save();
        // Mirror the frame horizontally to match the backend training data
        ctx.translate(drawWidth, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(video, 0, 0, drawWidth, drawHeight);
        ctx.restore();
        
        canvas.toBlob((blob) => {
          resolve(blob);
        }, 'image/jpeg', 0.8);
      });
    }
  }));

  // Active glow effect when hand is detected
  const glowClass = handDetected 
    ? 'border-accent-signal shadow-[0_0_20px_color-mix(in_srgb,var(--accent-signal)_30%,transparent)] motion-safe:transition-all' 
    : 'border-border';

  // Render logic based on status
  return (
    <div className={`relative w-full h-full bg-surface-raised border-2 rounded-2xl overflow-hidden flex flex-col items-center justify-center text-center ${glowClass}`}>
      
      {status === 'loading' && (
        <div className="p-4">
          <p className="text-text-primary">Requesting camera access...</p>
        </div>
      )}
      
      {status === 'denied' && (
        <div className="p-4 text-accent-warm">
          <p>Camera permission denied. Please allow access in your browser.</p>
        </div>
      )}
      
      {status === 'not_found' && (
        <div className="p-4 text-accent-warm">
          <p>No camera found. Please connect a webcam.</p>
        </div>
      )}
      
      {status === 'error' && (
        <div className="p-4 text-accent-warm">
          <p>An unexpected error occurred accessing the camera.</p>
        </div>
      )}
      
      {/* 
        Video element must always be in the DOM to attach the ref when stream becomes active.
        We hide it using CSS until status is active.
      */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className={`w-full h-full object-cover ${status === 'active' ? 'block' : 'hidden'} scale-x-[-1]`}
      />
      
      {/* Invisible offscreen canvas used solely for capturing JPEGs */}
      <canvas ref={canvasRef} className="hidden" />
      
    </div>
  );
});

WebcamFeed.displayName = 'WebcamFeed';

export default WebcamFeed;
