import React from 'react';

const CategoryPreferencePopup = ({ 
  category, 
  isAlreadySaved, 
  onSave, 
  onRemove, 
  onCancel 
}) => {
  const handleAction = () => {
    if (isAlreadySaved) {
      onRemove(category);
    } else {
      onSave(category);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex justify-center items-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-md w-full p-6">
        <div className="flex items-center mb-4">
          <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center mr-4">
            {isAlreadySaved ? (
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            )}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {isAlreadySaved ? 'Remove Category Preference' : 'Save Category Preference'}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Category: <span className="font-medium text-indigo-600 dark:text-indigo-400">{category}</span>
            </p>
          </div>
        </div>

        <div className="mb-6">
          <p className="text-gray-700 dark:text-gray-300">
            {isAlreadySaved ? (
              <>
                This category is currently saved to your preferences. 
                <span className="font-medium"> Do you want to remove it?</span>
              </>
            ) : (
              <>
                Would you like to save <span className="font-medium">"{category}"</span> to your preferences for quick access?
              </>
            )}
          </p>
          
          {!isAlreadySaved && (
            <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                💡 Saved categories will appear as quick filters at the top for easy access.
              </p>
            </div>
          )}
        </div>

        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors duration-200 font-medium"
          >
            Cancel
          </button>
          <button
            onClick={handleAction}
            className={`px-4 py-2 rounded-lg transition-colors duration-200 font-medium ${
              isAlreadySaved 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-indigo-600 hover:bg-indigo-700 text-white'
            }`}
          >
            {isAlreadySaved ? 'Remove' : 'Save Preference'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CategoryPreferencePopup;