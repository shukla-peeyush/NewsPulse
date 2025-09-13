import React from 'react';

const ErrorDisplay = ({ error, onRetry, showRetry = true }) => {
  const getErrorMessage = (error) => {
    if (typeof error === 'string') return error;
    if (error?.message) return error.message;
    return 'An unexpected error occurred';
  };

  const getErrorDetails = (error) => {
    if (error?.status === 0) {
      return {
        title: 'Connection Error',
        message: 'Unable to connect to the API server. Please check if the server is running.',
        suggestion: 'Make sure the API server is running on http://localhost:8000'
      };
    }
    
    if (error?.status >= 500) {
      return {
        title: 'Server Error',
        message: 'The server encountered an error while processing your request.',
        suggestion: 'Please try again in a few moments. If the problem persists, contact support.'
      };
    }
    
    if (error?.status === 404) {
      return {
        title: 'Not Found',
        message: 'The requested resource could not be found.',
        suggestion: 'Please check the URL or try refreshing the page.'
      };
    }
    
    if (error?.status >= 400) {
      return {
        title: 'Request Error',
        message: getErrorMessage(error),
        suggestion: 'Please check your request and try again.'
      };
    }
    
    return {
      title: 'Error',
      message: getErrorMessage(error),
      suggestion: 'Please try again or refresh the page.'
    };
  };

  const errorDetails = getErrorDetails(error);

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 text-center">
        {/* Error Icon */}
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/20 mb-4">
          <svg className="h-6 w-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        
        {/* Error Title */}
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          {errorDetails.title}
        </h3>
        
        {/* Error Message */}
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          {errorDetails.message}
        </p>
        
        {/* Error Suggestion */}
        <p className="text-xs text-gray-400 dark:text-gray-500 mb-6">
          {errorDetails.suggestion}
        </p>
        
        {/* Error Details (for debugging) */}
        {error?.status && (
          <div className="text-xs text-gray-400 dark:text-gray-500 mb-4 p-2 bg-gray-50 dark:bg-gray-700 rounded">
            Status: {error.status}
            {error?.details && (
              <div className="mt-1">
                Details: {JSON.stringify(error.details, null, 2)}
              </div>
            )}
          </div>
        )}
        
        {/* Retry Button */}
        {showRetry && onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-blue-500 dark:hover:bg-blue-600 transition-colors"
          >
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Try Again
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorDisplay;