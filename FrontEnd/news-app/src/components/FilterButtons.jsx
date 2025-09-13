import React from 'react';

const FilterButtons = ({ categories, activeFilter, onFilterChange }) => (
  <div className="flex items-center overflow-x-auto space-x-3 pb-4 mb-8">
    {categories.map(category => {
      const isActive = category === activeFilter;
      const buttonClasses = isActive 
        ? 'bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900' 
        : 'bg-white text-gray-800 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-700';
      
      return (
        <button 
          key={category} 
          onClick={() => onFilterChange(category)} 
          className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200 ${buttonClasses}`}
        >
          {category}
        </button>
      );
    })}
  </div>
);

export default FilterButtons;