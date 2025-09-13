import React from 'react';

const Loading = () => {
  return (
    <div className="flex justify-center items-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-100"></div>
      <span className="ml-3 text-gray-600 dark:text-gray-400">Loading articles...</span>
    </div>
  );
};

export default Loading;