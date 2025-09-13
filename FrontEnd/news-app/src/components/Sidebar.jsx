import React from 'react';

const Sidebar = ({ 
  categories, 
  savedCategories, 
  activeFilter, 
  onFilterChange,
  onRemoveCategory,
  isMobileOpen = false,
  onMobileClose
}) => {
  return (
    <>
      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden" 
          onClick={onMobileClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 lg:z-auto
        w-64 bg-gradient-to-b from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 
        border-r border-gray-200 dark:border-gray-700 shadow-lg lg:shadow-none
        h-full overflow-y-auto
        transform transition-transform duration-300 ease-in-out lg:transform-none
        ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Mobile Close Button */}
        <div className="lg:hidden flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Categories</h2>
          <button
            onClick={onMobileClose}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-6">
        {/* All Categories Section */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-900/30 dark:to-blue-900/30 rounded-lg p-3 mb-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center">
              <div className="w-8 h-8 bg-indigo-100 dark:bg-indigo-800 rounded-lg flex items-center justify-center mr-3">
                <svg className="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14-7H5m14 14H5" />
                </svg>
              </div>
              All Categories
            </h3>
          </div>
          <div className="space-y-2">
            {categories.map(category => {
              const isActive = category === activeFilter;
              return (
                <button
                  key={category}
                  onClick={() => onFilterChange(category)}
                  className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 group ${
                    isActive
                      ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-lg transform scale-105'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 dark:hover:from-gray-700 dark:hover:to-gray-600 hover:shadow-md hover:transform hover:scale-102'
                  }`}
                >
                  {category}
                </button>
              );
            })}
          </div>
        </div>

        {/* Saved Categories Section */}
        {savedCategories.length > 0 && (
          <div>
            <div className="bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-800/50 dark:to-slate-800/50 rounded-lg p-3 mb-4">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white flex items-center">
                <div className="w-6 h-6 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center mr-2">
                  <svg className="w-3 h-3 text-gray-600 dark:text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                </div>
                Saved Categories
              </h3>
            </div>
            <div className="space-y-2">
              {savedCategories.map(category => {
                const isActive = category === activeFilter;
                return (
                  <div key={category} className="flex items-center group">
                    <button
                      onClick={() => onFilterChange(category)}
                      className={`flex-1 text-left px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 ${
                        isActive
                          ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-lg transform scale-105'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 dark:hover:from-gray-700 dark:hover:to-gray-600 border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md hover:transform hover:scale-102'
                      }`}
                    >
                      ⭐ {category}
                    </button>
                    <button
                      onClick={() => onRemoveCategory(category)}
                      className="ml-2 p-1 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                      title="Remove from saved categories"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                );
              })}
            </div>
            
            {/* Saved Categories Info */}
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-xs text-blue-800 dark:text-blue-200">
                💡 Click on any category while browsing to save it here for quick access.
              </p>
            </div>
          </div>
        )}

        {/* Empty State for Saved Categories */}
        {savedCategories.length === 0 && (
          <div>
            <div className="bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-800/50 dark:to-slate-800/50 rounded-lg p-3 mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center">
                <div className="w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center mr-3">
                  <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                </div>
                Saved Categories
              </h3>
            </div>
            <div className="p-6 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-800/50 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 text-center">
              <div className="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">
                No saved categories yet
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                Click on any category to save it for quick access
              </p>
            </div>
          </div>
        )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;