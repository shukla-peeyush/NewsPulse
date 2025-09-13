import React, { useState, useEffect } from 'react';
import api from '../services/api';

const ApiStatus = () => {
  const [status, setStatus] = useState('checking');
  const [apiInfo, setApiInfo] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);

  const checkApiStatus = async () => {
    setStatus('checking');
    try {
      // Simple check of articles endpoint
      const response = await fetch('http://127.0.0.1:8002/articles');
      if (response.ok) {
        setApiInfo({ message: 'Articles API', version: '1.0.0' });
        setStatus('connected');
      } else {
        setStatus('error');
      }
    } catch (error) {
      setStatus('error');
    }
    setLastChecked(new Date());
  };

  useEffect(() => {
    checkApiStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkApiStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case 'connected': return 'text-green-600 dark:text-green-400';
      case 'error': return 'text-red-600 dark:text-red-400';
      case 'checking': return 'text-yellow-600 dark:text-yellow-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'connected':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      case 'checking':
        return (
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        );
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected': return 'API Connected';
      case 'error': return 'API Disconnected';
      case 'checking': return 'Checking...';
      default: return 'Unknown';
    }
  };

  return (
    <div className="flex items-center space-x-2 text-sm">
      <div className={`flex items-center space-x-1 ${getStatusColor()}`}>
        {getStatusIcon()}
        <span>{getStatusText()}</span>
      </div>
      
      {apiInfo && status === 'connected' && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          v{apiInfo.version}
        </div>
      )}
      
      {lastChecked && (
        <div className="text-xs text-gray-400 dark:text-gray-500">
          Last checked: {lastChecked.toLocaleTimeString()}
        </div>
      )}
      
      <button
        onClick={checkApiStatus}
        className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
        disabled={status === 'checking'}
      >
        Refresh
      </button>
    </div>
  );
};

export default ApiStatus;