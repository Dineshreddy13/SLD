import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useConnectionStore } from '../store/useConnectionStore';
import { useUIStore } from '../store/useUIStore';

const HandLogo = () => (
  <svg 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    className="text-accent-signal"
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 20v-8" />
    <path d="M12 12l-6-4" />
    <path d="M12 12l4-5" />
    <path d="M12 12l6 4" />
    <circle cx="12" cy="20" r="1.5" fill="currentColor" />
    <circle cx="12" cy="12" r="1.5" fill="currentColor" />
    <circle cx="6" cy="8" r="1.5" fill="currentColor" />
    <circle cx="16" cy="7" r="1.5" fill="currentColor" />
    <circle cx="18" cy="16" r="1.5" fill="currentColor" />
  </svg>
);

const Header = () => {
  const connectionStatus = useConnectionStore((state) => state.status);
  const darkMode = useUIStore((state) => state.darkMode);
  const toggleDarkMode = useUIStore((state) => state.toggleDarkMode);

  // Status configuration
  const statusConfig = {
    connected: { color: 'bg-accent-signal', text: 'Connected', animate: false },
    connecting: { color: 'bg-text-secondary', text: 'Connecting...', animate: true },
    disconnected: { color: 'bg-accent-warm', text: 'Disconnected', animate: false },
    error: { color: 'bg-accent-warm', text: 'Error', animate: false }
  };

  const currentStatus = statusConfig[connectionStatus] || statusConfig.disconnected;

  return (
    <header className="sticky top-0 z-50 w-full bg-surface/80 backdrop-blur-md border-b border-border">
      <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo and Wordmark */}
        <div className="flex items-center gap-3">
          <HandLogo />
          <span className="font-sans font-medium text-text-primary tracking-wide">SignDetect</span>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-4 sm:gap-6">
          
          {/* Connection Status Pill */}
          <div className="flex items-center gap-2 bg-surface-raised px-3 py-1.5 rounded-full border border-border">
            <span className="relative flex h-2.5 w-2.5">
              {currentStatus.animate && (
                <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 motion-safe:animate-ping ${currentStatus.color}`} />
              )}
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${currentStatus.color}`} />
            </span>
            <span className="text-xs font-mono font-medium tracking-wide text-text-primary hidden sm:inline-block">
              {currentStatus.text}
            </span>
          </div>

          {/* Dark Mode Toggle */}
          <button
            onClick={toggleDarkMode}
            aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            className="p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-surface-raised focus:outline-none focus:ring-2 focus:ring-accent-signal transition-colors"
          >
            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          
        </div>
      </div>
    </header>
  );
};

export default Header;
